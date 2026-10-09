document.addEventListener("DOMContentLoaded", async () => {
    // Элементы управления графиком
    const canvas = document.getElementById("reportChart");
    const weekLabel = document.querySelector(".week-switch span");
    const prevBtn = document.getElementById("prevWeek");
    const nextBtn = document.getElementById("nextWeek");
    const periodBtns = document.querySelectorAll(".period-btn");

    // Элементы вкладок и таблицы
    const tabs = document.querySelectorAll(".tab");
    const tabContents = document.querySelectorAll(".tab-content");
    const detailTableBody = document.getElementById("detail-table-body");

    if (!canvas || !weekLabel || !prevBtn || !nextBtn) return;

    const ctx = canvas.getContext("2d");
    let chart;
    let currentPeriod = "week";
    let offset = 0;

    // --- ЛОГИКА ПЕРЕКЛЮЧЕНИЯ ВКЛАДОК ---

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const target = tab.dataset.target;

            // Визуальное переключение активной вкладки
            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            // Переключение видимости контента
            tabContents.forEach(content => {
                if (content.id === target) {
                    content.classList.remove("d-none");
                } else {
                    content.classList.add("d-none");
                }
            });

            // Если выбрали детали, грузим таблицу
            if (target === "detail-section") {
                fetchDetailData();
            } else {
                updateChart(); // Обновляем график при возврате на Summary
            }
        });
    });

    // --- ФУНКЦИИ ДЛЯ SUMMARY (ГРАФИК) ---

    function formatDate(date) {
        return date.toLocaleDateString("ru-RU", { day: "2-digit", month: "short" });
    }

    async function fetchData() {
        try {
            const res = await fetch(`/report/data/?period=${currentPeriod}&offset=${offset}`);
            if (!res.ok) throw new Error("Ошибка загрузки данных");
            return await res.json();
        } catch (err) {
            console.error(err);
            return [];
        }
    }

    function renderChart(labels, values) {
        if (chart) chart.destroy();

        chart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Концентрация Pomodoro",
                    data: values,
                    backgroundColor: "rgba(155, 17, 30, 0.4)",
                    borderColor: "rgba(155, 17, 30, 1)",
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, color: "#768390" },
                        grid: { color: "rgba(255, 255, 255, 0.05)" }
                    },
                    x: {
                        ticks: { color: "#768390" },
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    function updatePeriodLabel() {
        const today = new Date();
        let startDate, endDate;

        if (currentPeriod === "week") {
            startDate = new Date(today);
            const dayDiff = today.getDay() === 0 ? 6 : today.getDay() - 1;
            startDate.setDate(today.getDate() - dayDiff + (offset * 7));

            endDate = new Date(startDate);
            endDate.setDate(startDate.getDate() + 6);

            weekLabel.textContent = offset === 0 ? "Эта неделя" : `${formatDate(startDate)} — ${formatDate(endDate)}`;
        }
        else if (currentPeriod === "month") {
            startDate = new Date(today.getFullYear(), today.getMonth() + offset, 1);
            const monthName = startDate.toLocaleString('ru-RU', { month: 'long', year: 'numeric' });
            weekLabel.textContent = monthName.charAt(0).toUpperCase() + monthName.slice(1);
        }
        else if (currentPeriod === "year") {
            const targetYear = today.getFullYear() + offset;
            weekLabel.textContent = `${targetYear} год`;
        }

        nextBtn.disabled = offset >= 0;
    }

    async function updateChart() {
        const data = await fetchData();
        let labels = [];
        let values = [];

        if (currentPeriod === "week") {
            labels = data.map(d => d.day);
            values = data.map(d => d.count);
        }
        else if (currentPeriod === "month") {
            labels = ["1-7", "8-14", "15-21", "22+"];
            values = [0, 0, 0, 0];

            data.forEach(d => {
                const day = new Date(d.date).getDate();
                if (day <= 7) values[0] += d.count;
                else if (day <= 14) values[1] += d.count;
                else if (day <= 21) values[2] += d.count;
                else values[3] += d.count;
            });
        }
        else if (currentPeriod === "year") {
            labels = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"];
            values = Array(12).fill(0);

            data.forEach(d => {
                const monthIndex = new Date(d.date).getMonth();
                values[monthIndex] += d.count;
            });
        }

        renderChart(labels, values);
        updatePeriodLabel();
    }

    // --- ФУНКЦИИ ДЛЯ DETAIL (ТАБЛИЦА) ---

    async function fetchDetailData() {
        try {
            const res = await fetch('/report/report_detail/');
            if (!res.ok) throw new Error("Ошибка загрузки");

            const data = await res.json();

            // Очищаем таблицу перед отрисовкой
            detailTableBody.innerHTML = "";

            if (data.length === 0) {
                detailTableBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">Данных пока нет</td></tr>`;
                return;
            }

            data.forEach(item => {
                const row = `
                    <tr>
                        <td>
                            <div class="fw-bold">${item.date_display}</div>
                            <div class="text-muted small">${item.time_display}</div>
                        </td>
                        <td>
                            <span class="badge bg-secondary-subtle text-dark me-2">${item.task_label}</span>
                            <span class="fw-bold">${item.item_name}</span>
                        </td>
                        <td class="">${item.duration} min</td>
                        <td>
                            <button class="btn btn-link text-muted p-0">
                                <i class="bi bi-three-dots-vertical"></i>
                            </button>
                        </td>
                    </tr>
                `;
                detailTableBody.insertAdjacentHTML("beforeend", row);
            });
        } catch (err) {
            console.error("Ошибка:", err);
            detailTableBody.innerHTML = `<tr><td colspan="4" class="text-center text-danger">Не удалось загрузить данные</td></tr>`;
        }
    }

    // --- ОБРАБОТЧИКИ СОБЫТИЙ ---

    periodBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            periodBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            currentPeriod = btn.dataset.period;
            offset = 0;
            updateChart();
        });
    });

    prevBtn.addEventListener("click", () => {
        offset -= 1;
        updateChart();
    });

    nextBtn.addEventListener("click", () => {
        if (offset < 0) {
            offset += 1;
            updateChart();
        }
    });

    // Инициализация при первой загрузке
    updateChart();
});