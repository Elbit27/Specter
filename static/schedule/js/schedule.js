document.addEventListener("DOMContentLoaded", () => {
    // todayIndex - это индекс дня, для которого разрешен ввод (0=Пн, 6=Вс)
    const todayIndex = new Date().getDay() === 0 ? 6 : new Date().getDay() - 1;

    // === СЧИТАЕМ ИТОГО ===
    function updateTotals() {
        const totalCells = document.querySelectorAll(".total-row td.day-col");
        const dayCount = totalCells.length;

        for (let day = 0; day < dayCount; day++) {
            let sum = 0;

            document.querySelectorAll(`input[data-day="${day}"]`).forEach(input => {
                const value = parseInt(input.value);
                if (!isNaN(value)) sum += value;
            });

            const totalCell = document.getElementById(`total-${day}`);
            if (totalCell) totalCell.textContent = sum;
        }
    }

    // === НАСТРОЙКА INPUT ===
    document.querySelectorAll(".day-input").forEach(input => {
        const day = parseInt(input.dataset.day);
        if (isNaN(day)) return;

        // сохраняем старое значение для расчета 'diff'
        input.dataset.prev = input.value || 0;

        // ЛОГИКА БЛОКИРОВКИ: Разрешаем ввод только для текущего дня
        if (day !== todayIndex) {
            input.disabled = true;
            input.classList.add("disabled");
            return;
        }

        input.classList.add("active");

        // === ОТПРАВКА ИЗМЕНЕНИЙ (С ОБРАБОТКОЙ УСПЕХА) ===
        input.addEventListener("change", () => {
            const newValue = parseInt(input.value) || 0;
            const oldValue = parseInt(input.dataset.prev) || 0;
            const diff = newValue - oldValue;

            const tr = input.closest("tr");
            if (!tr) return;

            const itemId = tr.dataset.itemId;

            fetch("/schedule/update_poma/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: `item_id=${encodeURIComponent(itemId)}&day=${encodeURIComponent(day)}&diff=${encodeURIComponent(diff)}`
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                // УСПЕХ: Обновляем UI
                input.dataset.prev = newValue;
                updateTotals();
            })
            .catch(err => {
                console.error("❌ Fetch error or server side error:", err);
                // ОШИБКА: Откатываем UI на старое значение
                input.value = oldValue;
                updateTotals();
            });
        });
    });

    // первый расчёт
    updateTotals();
});


// === CSRF COOKIE ===
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}