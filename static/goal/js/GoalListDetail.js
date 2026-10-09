function recalculateProgress(card) {
    const progressContainer = card.querySelector('.goal-progress-container');
    if (!progressContainer) return;

    const fill = card.querySelector('.progress-bar-fill');
    const text = card.querySelector('.progress-percentage-text');

    if (fill && fill.style.width && fill.style.width !== "0%" && !progressContainer.dataset.totalSteps) {
        return;
    }

    let total = parseInt(progressContainer.dataset.totalSteps) || 0;
    let completed = parseInt(progressContainer.dataset.completedSteps) || 0;

    if (total === 0) {
        if (fill) fill.style.width = '0%';
        if (text) text.textContent = '0%';
        return;
    }

    const percentage = Math.round((completed / total) * 100);

    if (fill) fill.style.width = `${percentage}%`;
    if (text) text.textContent = `${percentage}%`;
}


document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('goal-modal');
    const closeBtn = document.getElementById('close-modal-btn');

    const stepModal = document.getElementById('step-detail-modal');
    const closeStepBtn = document.getElementById('close-step-modal-btn');
    const saveStepDescBtn = document.getElementById('save-step-desc-btn');

    let numericGoalData = { id: null, target: 0 };
    let currentGoalId = null;

    function refreshGoalModalData(goalId) {
        fetch(`/goal/api/goals/${goalId}/`)
            .then(response => response.json())
            .then(goal => {
                // Сборка списка ВЫПОЛНЕННЫХ шагов
                const completedContainer = document.getElementById('modal-steps-completed');
                completedContainer.innerHTML = '';
                const completedSteps = goal.steps ? goal.steps.filter(step => step.completed === true) : [];

                const completedCountEl = document.getElementById('modal-completed-count');
                if (completedCountEl) {
                    completedCountEl.textContent = completedSteps.length;
                }


                if (completedSteps.length > 0) {
                    completedSteps.forEach(step => {
                        const li = document.createElement('li');
                        li.className = 'modal-step-item completed-item';
                        li.style.cursor = 'pointer';
                        const truncatedTitle = step.title.length > 20
                            ? step.title.substring(0, 17) + '...'
                            : step.title;

                        li.innerHTML = `
                            <div class="modal-step-title" style="text-decoration: line-through; opacity: 0.6; display: flex; justify-content: space-between; align-items: center; width: 100%;">
                                <span>${truncatedTitle}</span>
                                <div class="step-actions-inline" style="opacity: 1; pointer-events: auto;">
                                    <button type="button" class="btn-step-action btn-modal-step-toggle" title="Вернуть в работу">
                                        <i class="bi bi-check-circle-fill" style="color: #2ecc71;"></i>
                                    </button>
                                </div>
                            </div>
                        `;

                        const toggleBtn = li.querySelector('.btn-modal-step-toggle');
                        toggleBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            updateStepStatusInModal(step.id, false); // Переводим в false (uncompleted)
                        });

                        li.addEventListener('click', () => {
                            document.getElementById('edit-step-id').value = step.id;
                            document.getElementById('step-modal-title').textContent = step.title;
                            document.getElementById('step-modal-desc').value = step.description || '';
                            stepModal.classList.add('active');
                        });

                        completedContainer.appendChild(li);
                    });
                } else {
                    completedContainer.innerHTML = '<li style="color: #999; font-style: italic; padding-left: 14px;">Нет выполненных шагов.</li>';
                }

                // Сборка списка НЕВЫПОЛНЕННЫХ шагов
                const uncompletedContainer = document.getElementById('modal-steps-uncompleted');
                uncompletedContainer.innerHTML = '';
                const uncompletedSteps = goal.steps ? goal.steps.filter(step => step.completed === false) : [];

                if (uncompletedSteps.length > 0) {
                    uncompletedSteps.forEach(step => {
                        const li = document.createElement('li');
                        li.className = 'modal-step-item';
                        li.style.cursor = 'pointer';
                        const truncatedTitle = step.title.length > 20
                            ? step.title.substring(0, 17) + '...'
                            : step.title;

                        li.innerHTML = `<div class="modal-step-title">${truncatedTitle}</div>`;

                        li.addEventListener('click', () => {
                            document.getElementById('edit-step-id').value = step.id;
                            document.getElementById('step-modal-title').textContent = step.title;
                            document.getElementById('step-modal-desc').value = step.description || '';
                            stepModal.classList.add('active');
                        });

                        uncompletedContainer.appendChild(li);
                    });
                } else {
                    uncompletedContainer.innerHTML = '<li style="color: #999; font-style: italic;">Все задачи выполнены! 🎉</li>';
                }
            });
    }

    // Открытие главной модалки (goal)
    document.querySelectorAll('.goal-card').forEach(card => {
        if (typeof recalculateProgress === 'function' && card.dataset.type !== 'numeric') {
            recalculateProgress(card);
        }

        card.addEventListener('click', function(e) {
            if (e.target.classList.contains('btn-action-edit') || e.target.closest('.btn-step-action')) {
                return;
            }

            const goalId = this.dataset.id;
            if (!goalId) return;
            currentGoalId = goalId;

            fetch(`/goal/api/goals/${goalId}/`)
                .then(response => response.json())
                .then(goal => {
                    document.getElementById('modal-title').textContent = goal.title;
                    document.getElementById('modal-desc').textContent = goal.description || 'Без описания';
                    document.getElementById('modal-edit-btn').href = `/goal/${goal.id}/edit/`;

                    const prizeWrapper = document.getElementById('modal-prize-wrapper');
                    if (goal.prize) {
                        document.getElementById('modal-prize').textContent = goal.prize;
                        prizeWrapper.style.display = 'block';
                    } else {
                        prizeWrapper.style.display = 'none';
                    }

                    const stepsBlock = document.getElementById('modal-steps-block');
                    const numericBlock = document.getElementById('modal-numeric-block');

                    if (goal.goal_type === 'numeric') {
                        if (stepsBlock) stepsBlock.style.display = 'none';
                        if (numericBlock) numericBlock.style.display = 'block';

                        const numInput = document.getElementById('modal-numeric-input');
                        const numTarget = document.getElementById('modal-numeric-target');
                        if (numInput) numInput.value = goal.current_value;
                        if (numTarget) numTarget.textContent = goal.target_value;

                        numericGoalData.id = goal.id;
                        numericGoalData.target = goal.target_value;
                    } else {
                        if (numericBlock) numericBlock.style.display = 'none';
                        if (stepsBlock) stepsBlock.style.display = 'block';

                        const toggleBtn = document.getElementById('modal-toggle-completed-btn');
                        if (toggleBtn) {
                            toggleBtn.classList.remove('active');
                            toggleBtn.innerHTML = `<span class="toggle-icon">✓</span> Выполненные задачи (<span id="modal-completed-count">0</span>)`;
                        }

                        // Обновляем списки шагов для списочной цели
                        refreshGoalModalData(currentGoalId);
                    }

                    modal.classList.add('active');
                })
                .catch(err => console.error('Ошибка при загрузке данных:', err));
        });
    });


    const numInput = document.getElementById('modal-numeric-input');
    const saveStatus = document.getElementById('numeric-save-status');

    if (numInput) {
        numInput.addEventListener('change', async () => {
            const newValue = parseInt(numInput.value) || 0;

            if (saveStatus) {
                saveStatus.style.color = '#e67e22';
                saveStatus.textContent = 'Сохранение...';
            }

            try {
                const currentGoalResp = await fetch(`/goal/api/goals/${numericGoalData.id}/`);
                if (!currentGoalResp.ok) throw new Error('Не удалось получить данные');

                const fullGoalData = await currentGoalResp.json();

                // Ограничиваем ввод по таргету (опционально, если нельзя перевыполнять)
                let finalValue = newValue;
                if (finalValue < 0) finalValue = 0;
                if (finalValue > numericGoalData.target) finalValue = numericGoalData.target;

                numInput.value = finalValue;

                fullGoalData.current_value = finalValue;

                // Отправил обновленный пакет обратно на бэкенд через PUT
                const response = await fetch(`/goal/api/goals/${numericGoalData.id}/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': typeof CSRF_TOKEN !== 'undefined' ? CSRF_TOKEN : getCookie('csrftoken')
                    },
                    body: JSON.stringify(fullGoalData)
                });

                if (response.ok) {
                    if (saveStatus) {
                        saveStatus.style.color = '#2ecc71';
                        saveStatus.textContent = '✓ Изменения сохранены!';
                    }

                    const mainCard = document.querySelector(`.goal-card[data-id="${numericGoalData.id}"]`);
                    if (mainCard) {
                        // Ищем текстовый счетчик "13 / 20" внутри карточки
                        const counterDiv = mainCard.querySelector('.goal-steps-section div');
                        if (counterDiv) {
                            counterDiv.innerHTML = `${finalValue} <span style="color: #888; font-size: 1rem; font-weight: normal;">/ ${numericGoalData.target}</span>`;
                        }

                        // Вычисляем новый процент для прогресс-бара
                        const newPct = Math.round((finalValue / numericGoalData.target) * 100);
                        const fillBar = mainCard.querySelector('.progress-bar-fill');
                        const pctText = mainCard.querySelector('.progress-percentage-text');

                        if (fillBar) fillBar.style.width = `${newPct}%`;
                        if (pctText) pctText.textContent = `${newPct}%`;
                    }

                } else {
                    if (saveStatus) {
                        saveStatus.style.color = '#e74c3c';
                        saveStatus.textContent = '❌ Ошибка сервера при сохранении';
                    }
                }
            } catch (error) {
                console.error('Ошибка автосохранения:', error);
                if (saveStatus) {
                    saveStatus.style.color = '#e74c3c';
                    saveStatus.textContent = '❌ Ошибка сети';
                }
            }
        });
    }

    // При закрытии модального окна очищаем текст статуса сохранения
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('active');
            if (saveStatus) saveStatus.textContent = '';
        });
    }

    // ЗАКРЫТИЕ ПЕРВОГО МОДАЛЬНОГО ОКНА
    if (closeBtn) {
        closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    }
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.remove('active');
        });
    }

    // ЗАКРЫТИЕ ВТОРОГО МОДАЛЬНОГО ОКНА (ДЛЯ ШАГА)
    if (closeStepBtn) {
        closeStepBtn.addEventListener('click', () => stepModal.classList.remove('active'));
    }
    if (stepModal) {
        stepModal.addEventListener('click', (e) => {
            if (e.target === stepModal) stepModal.classList.remove('active');
        });
    }

    // СОХРАНЕНИЕИЕ ИЗМЕНЕННОГО ОПИСАНИЯ ШАГА
    if (saveStepDescBtn) {
        saveStepDescBtn.addEventListener('click', () => {
            const stepId = document.getElementById('edit-step-id').value;
            const newDescription = document.getElementById('step-modal-desc').value;

            if (!stepId) return;

            // Отправляем асинхронный PATCH запрос в StepViewSet на бэкенд
            fetch(`/goal/api/steps/${stepId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN
                },
                body: JSON.stringify({ description: newDescription })
            })
            .then(response => {
                if (response.ok) {
                    console.log(`Описание шага ${stepId} успешно обновлено в базе данных`);
                    stepModal.classList.remove('active');

                    if (currentGoalId) {
                        refreshGoalModalData(currentGoalId);
                    }
                } else {
                    console.error('Ошибка при сохранении описания шага на бэкенде');
                }
            })
            .catch(err => console.error('Ошибка сети при обновлении описания:', err));
        });
    }

    // Кнопка отметки выполнения... on main goal-card position
    document.querySelectorAll('.btn-step-complete').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();

            const stepItem = this.closest('.step-item');
            const stepId = stepItem.dataset.stepId;
            const icon = this.querySelector('i');
            const goalCard = stepItem.closest('.goal-card');
            const progressContainer = goalCard ? goalCard.querySelector('.goal-progress-container') : null;

            const isCurrentlyCompleted = stepItem.classList.toggle('completed');

            if (isCurrentlyCompleted) {
                icon.classList.remove('bi-circle');
                icon.classList.add('bi-check-circle-fill');
                if (progressContainer) {
                    let currentCompleted = parseInt(progressContainer.dataset.completedSteps) || 0;
                    progressContainer.dataset.completedSteps = currentCompleted + 1;
                }
            } else {
                icon.classList.remove('bi-check-circle-fill');
                icon.classList.add('bi-circle');
                if (progressContainer) {
                    let currentCompleted = parseInt(progressContainer.dataset.completedSteps) || 0;
                    progressContainer.dataset.completedSteps = Math.max(0, currentCompleted - 1);
                }
            }

            if (goalCard) {
                recalculateProgress(goalCard);
            }

            fetch(`/goal/api/steps/${stepId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN
                },
                body: JSON.stringify({ completed: isCurrentlyCompleted })
            })
            .then(response => {
                if (response.ok) {
                    console.log(`Статус шага ${stepId} изменен в БД`);
                    const goalCard = stepItem.closest('.goal-card');
                    if (goalCard && typeof recalculateProgress === 'function') {
                        recalculateProgress(goalCard);
                    }
                } else {
                    stepItem.classList.toggle('completed');
                    console.error('Бэкенд вернул ошибку при сохранении статуса.');
                }
            })
            .catch(err => console.error('Ошибка сети:', err));
        });
    });

    // Кнопка спойлер
    const toggleCompletedBtn = document.getElementById('modal-toggle-completed-btn');
    if (toggleCompletedBtn) {
        toggleCompletedBtn.addEventListener('click', function() {
            const isActive = this.classList.toggle('active');
            const count = document.getElementById('modal-completed-count').textContent;

            if (isActive) {
                this.innerHTML = `<span class="toggle-icon">▼</span> Скрыть завершенные шаги (${count})`;
            } else {
                this.innerHTML = `<span class="toggle-icon">▶</span> Показать завершенные шаги (${count})`;
            }
        });
    }

    // Функция-хэлпер для отправки PATCH запроса из модалки
    function updateStepStatusInModal(stepId, newStatus) {
        fetch(`/goal/api/steps/${stepId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN
            },
            body: JSON.stringify({ completed: newStatus })
        })
        .then(response => {
            if (response.ok) {
                console.log(`Статус шага ${stepId} изменен в модалке на ${newStatus}`);
                // Перерисовываем списки в модальном окне, чтобы шаг перелетел в нужный блок
                if (currentGoalId) {
                    refreshGoalModalData(currentGoalId);
                    // Авто-обновление главной карточки на странице
                    const mainCard = document.querySelector(`.goal-card[data-id="${currentGoalId}"]`);
                    if (mainCard) {
                        const progressContainer = mainCard.querySelector('.goal-progress-container');
                        if (progressContainer) {
                            let currentCompleted = parseInt(progressContainer.dataset.completedSteps) || 0;

                            if (newStatus === true) {
                                progressContainer.dataset.completedSteps = currentCompleted + 1;
                            } else {
                                progressContainer.dataset.completedSteps = Math.max(0, currentCompleted - 1);
                            }
                            if (typeof recalculateProgress === 'function') {
                                recalculateProgress(mainCard);
                            }
                        }
                        updateMainCardStepsUI(mainCard, currentGoalId);
                    }
                }
            } else {
                console.error('Не удалось обновить статус шага из модального окна.');
            }
        })
        .catch(err => console.error('Ошибка сети:', err));
    }

    function updateMainCardStepsUI(card, goalId) {
        fetch(`/goal/api/goals/${goalId}/`)
            .then(response => response.json())
            .then(goal => {
                const stepsSection = card.querySelector('.goal-steps-section');
                if (!stepsSection) return;

                const uncompletedSteps = goal.steps ? goal.steps.filter(step => step.completed === false) : [];

                if (uncompletedSteps.length > 0) {
                    const visibleSteps = uncompletedSteps.slice(0, 2);

                    let stepsHtml = '<ul class="steps-list">';
                    visibleSteps.forEach(step => {
                        stepsHtml += `
                            <li class="step-item" data-step-id="${step.id}">
                                <div class="step-item-main">
                                    <span class="step-item-title">${step.title}</span>
                                    <div class="step-actions-inline">
                                        <button type="button" class="btn-step-action btn-step-complete" title="Отметить выполненным">
                                            <i class="bi bi-circle"></i>
                                        </button>
                                    </div>
                                </div>
                            </li>
                        `;
                    });
                    stepsHtml += '</ul>';

                    if (uncompletedSteps.length > 2) {
                        stepsHtml += '<div class="steps-more-dots" style="padding-left: 10px; font-weight: bold; color: #888; letter-spacing: 2px;">...</div>';
                    }

                    stepsSection.innerHTML = stepsHtml;
                    rebindMainCardSignals(card);

                } else {
                    stepsSection.innerHTML = '<p class="no-steps">План действий пуст.</p>';
                }
            });
    }

    function rebindMainCardSignals(card) {
        card.querySelectorAll('.btn-step-complete').forEach(button => {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                window.location.reload();
            });
        });
    }
});
