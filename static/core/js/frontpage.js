document.addEventListener("DOMContentLoaded", () => {
    const display = document.getElementById("pomo-timer");
    const toggleBtn = document.getElementById("pomo-toggle");
    const resetBtn = document.getElementById("pomo-reset");
    const progressFill = document.getElementById("pomo-progress");
    const tabs = document.querySelectorAll(".pomo-tab");

    let currentMinutes = 60;
    let totalSeconds = currentMinutes * 60;
    let timeLeft = totalSeconds;
    let timerId = null;

    function updateUI() {
        const mins = Math.floor(timeLeft / 60);
        const secs = timeLeft % 60;
        const formatted = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;

        display.textContent = formatted;
        document.title = timerId ? `${formatted} — Specter` : "Specter — Интеллектуальный ассистент продуктивности";

        const percent = ((totalSeconds - timeLeft) / totalSeconds) * 100;
        progressFill.style.width = `${percent}%`;
    }

    function playNotificationSound() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const pattern = [
                { freq: 659.25, time: 0.00, dur: 0.35 }, // E5
                { freq: 880.00, time: 0.14, dur: 0.65 }, // A5
                { freq: 659.25, time: 0.90, dur: 0.35 }, // E5
                { freq: 880.00, time: 1.04, dur: 0.85 }, // A5
            ];

            pattern.forEach(({ freq, time, dur }) => {
                const start = ctx.currentTime + time;
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();

                osc.type = "sine";
                osc.frequency.setValueAtTime(freq, start);

                gain.gain.setValueAtTime(0.001, start);
                gain.gain.linearRampToValueAtTime(0.18, start + 0.02);
                gain.gain.exponentialRampToValueAtTime(0.0001, start + dur);

                osc.connect(gain);
                gain.connect(ctx.destination);

                osc.start(start);
                osc.stop(start + dur);
            });
        } catch (e) {}
    }

    function stopTimer() {
        clearInterval(timerId);
        timerId = null;
        toggleBtn.textContent = "Старт";
        toggleBtn.classList.remove("is-running");
    }

    toggleBtn.addEventListener("click", () => {
        if (timerId) {
            stopTimer();
        } else {
            toggleBtn.textContent = "Пауза";
            toggleBtn.classList.add("is-running");
            timerId = setInterval(() => {
                if (timeLeft > 0) {
                    timeLeft--;
                    updateUI();
                } else {
                    stopTimer();
                    playNotificationSound();
                }
            }, 1000);
        }
    });

    resetBtn.addEventListener("click", () => {
        stopTimer();
        timeLeft = totalSeconds;
        updateUI();
    });

    tabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            tabs.forEach((t) => t.classList.remove("active"));
            tab.classList.add("active");

            stopTimer();
            currentMinutes = parseInt(tab.dataset.minutes, 10);
            totalSeconds = currentMinutes * 60;
            timeLeft = totalSeconds;
            updateUI();
        });
    });

    updateUI();
});
