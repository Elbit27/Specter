document.addEventListener('DOMContentLoaded', () => {
    const stepsContainer = document.getElementById('steps-container');
    const addStepBtn = document.getElementById('add-step-btn');
    const goalForm = document.getElementById('goal-form');

    const colorInput = document.getElementById('card_color');
    const colorPreview = document.getElementById('color-preview-circle');
    const colorHexText = document.getElementById('color-hex-text');

    if (colorPreview && colorInput) {
        colorPreview.addEventListener('click', () => colorInput.click());
    }

    if (colorInput) {
        colorInput.addEventListener('input', (e) => {
            const selectedColor = e.target.value;
            if (colorPreview) colorPreview.style.backgroundColor = selectedColor;
            if (colorHexText) colorHexText.textContent = selectedColor;
            const previewBar = document.getElementById('preview-progress-bar');
            if (previewBar) previewBar.style.backgroundColor = selectedColor;
        });
    }

    function createStepHTML() {
        const stepDiv = document.createElement('div');
        stepDiv.className = 'step-card';
        stepDiv.innerHTML = `
            <div class="step-header">
                <h3>Новый шаг</h3>
                <button type="button" class="btn-delete" onclick="this.closest('.step-card').remove()">Удалить</button>
            </div>
            <div class="form-group">
                <label>Название шага</label>
                <input type="text" class="step-title" required>
            </div>
            <div class="form-group">
                <label>Описание</label>
                <textarea class="step-description" rows="2"></textarea>
            </div>
        `;
        return stepDiv;
    }

    if (addStepBtn) {
        addStepBtn.addEventListener('click', () => {
            if (stepsContainer) stepsContainer.appendChild(createStepHTML());
        });
    }

    const cvInp = document.getElementById('current_value');
    const tvInp = document.getElementById('target_value');
    if (cvInp && tvInp) {
        const calcPreview = () => {
            const current = parseFloat(cvInp.value) || 0;
            const target = parseFloat(tvInp.value) || 1;
            const bar = document.getElementById('preview-progress-bar');
            const txt = document.getElementById('preview-progress-percent');
            let pct = Math.round((current / target) * 100);
            pct = Math.max(0, Math.min(100, pct));
            if (bar) bar.style.width = pct + '%';
            if (txt) txt.innerText = pct + '%';
        };
        cvInp.addEventListener('input', calcPreview);
        tvInp.addEventListener('input', calcPreview);
    }

    const activeRadio = document.querySelector('input[name="goal_type"]:checked');
    if (activeRadio) window.toggleGoalType(activeRadio.value);

    if (goalForm) {
        goalForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const goalId = document.getElementById('goal-id') ? document.getElementById('goal-id').value : '';
            const goalType = document.querySelector('input[name="goal_type"]:checked').value;
            const stepsData = [];

            if (goalType === 'steps') {
                document.querySelectorAll('.step-card').forEach(card => {
                    const titleInp = card.querySelector('.step-title');
                    const descInp = card.querySelector('.step-description');
                    if (titleInp) {
                        stepsData.push({
                            id: card.dataset.stepId ? parseInt(card.dataset.stepId) : null,
                            title: titleInp.value,
                            description: descInp ? descInp.value : '',
                            completed: card.dataset.completed === 'true'
                        });
                    }
                });
            }

            const payload = {
                title: document.getElementById('title').value,
                description: document.getElementById('description').value,
                card_color: colorInput ? colorInput.value : '#4a90e2',
                prize: document.getElementById('prize') ? document.getElementById('prize').value : '',
                goal_type: goalType,
                current_value: parseInt(document.getElementById('current_value').value) || 0,
                target_value: parseInt(document.getElementById('target_value').value) || 100,
                steps: stepsData
            };

            const isEdit = !!goalId;
            const url = !isEdit ? '/goal/api/goals/' : `/goal/api/goals/${goalId}/`;
            const method = isEdit ? 'PUT' : 'POST';
            const token = typeof CSRF_TOKEN !== 'undefined' ? CSRF_TOKEN : getCookie('csrftoken');

            try {
                const response = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
                    body: JSON.stringify(payload)
                });
                if (response.ok) {
                    alert(isEdit ? 'Цель успешно обновлена!' : 'Цель создана!');
                    window.location.href = '/goal/';
                } else {
                    alert('Ошибка сохранения данных!');
                }
            } catch (err) {
                alert('Сетевая ошибка!');
            }
        });
    }
});

window.toggleGoalType = function(type) {
    const sSec = document.getElementById('section-steps-type');
    const nSec = document.getElementById('section-numeric-type');
    const sLbl = document.getElementById('type-steps-label');
    const nLbl = document.getElementById('type-numeric-label');
    if (!sSec || !nSec) return;

    if (type === 'steps') {
        sSec.style.display = 'block'; nSec.style.display = 'none';
        if (sLbl) sLbl.style.borderColor = '#4a90e2'; if (nLbl) nLbl.style.borderColor = '#ccc';
        document.querySelectorAll('.step-title').forEach(el => el.required = true);
    } else {
        sSec.style.display = 'none'; nSec.style.display = 'block';
        if (nLbl) nLbl.style.borderColor = '#4a90e2'; if (sLbl) sLbl.style.borderColor = '#ccc';
        document.querySelectorAll('.step-title').forEach(el => el.required = false);
        const cv = document.getElementById('current_value');
        if (cv) cv.dispatchEvent(new Event('input'));
    }
};

window.deleteGoal = async function(goalId) {
    if (!confirm("Удалить цель?")) return;
    try {
        const response = await fetch(`/goal/api/goals/${goalId}/`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' }
        });
        if (response.ok) window.location.href = '/goal/';
    } catch (e) { alert("Ошибка удаления!"); }
};

function getCookie(name) {
    let value = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const c = cookies[i].trim();
            if (c.substring(0, name.length + 1) === (name + '=')) {
                value = decodeURIComponent(c.substring(name.length + 1)); break;
            }
        }
    }
    return value;
}
