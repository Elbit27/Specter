document.addEventListener('DOMContentLoaded', () => {
    const avatarInput = document.getElementById('id_avatar');
    const avatarImg = document.querySelector('.profile-avatar');
    const avatarPlaceholder = document.querySelector('.avatar-placeholder');
    const profileForm = document.querySelector('.profile-form');
    const saveBtn = document.querySelector('.btn-save');

    // 1. ДИНАМИЧЕСКОЕ ПРЕВЬЮ АВАТАРА
    if (avatarInput) {
        avatarInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                // Проверяем тип файла
                if (!file.type.startsWith('image/')) {
                    showToast('Можно загружать только изображения', 'error');
                    this.value = '';
                    return;
                }

                const reader = new FileReader();
                reader.onload = function(e) {
                    if (avatarImg) {
                        // Если тег img уже существует, меняем src
                        avatarImg.src = e.target.result;
                    } else if (avatarPlaceholder) {
                        // Если был плейсхолдер с буквой, заменяем его на полноценный img
                        const newImg = document.createElement('img');
                        newImg.src = e.target.result;
                        newImg.alt = 'Аватар';
                        newImg.classList.add('profile-avatar');
                        avatarPlaceholder.parentNode.replaceChild(newImg, avatarPlaceholder);
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // 2. АСИНХРОННАЯ ОТПРАВКА ФОРМЫ (AJAX)
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // Блокируем стандартную перезагрузку страницы

            // Клиентская валидация Email
            const emailInput = document.getElementById('id_email');
            if (emailInput && !validateEmail(emailInput.value)) {
                showToast('Введите корректный Email адрес', 'error');
                return;
            }

            // Визуальный лоадер на кнопке
            const originalBtnText = saveBtn.textContent;
            saveBtn.textContent = 'Сохранение...';
            saveBtn.disabled = true;

            // Собираем данные (включая файлы)
            const formData = new FormData(profileForm);

            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        // Django требует этот заголовок для AJAX POST-запросов
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    showToast('Профиль успешно обновлен!', 'success');
                    // Если в шапке сайта тоже есть аватарка/имя, обновляем их
                    const topNavUsername = document.querySelector('.nav-username');
                    if (topNavUsername && formData.get('username')) {
                        topNavUsername.textContent = formData.get('username');
                    }
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    showToast(errorData.error || 'Ошибка при сохранении данных', 'error');
                }
            } catch (error) {
                console.error('Error saving profile:', error);
                showToast('Не удалось связаться с сервером', 'error');
            } finally {
                // Возвращаем кнопку в исходное состояние
                saveBtn.textContent = originalBtnText;
                saveBtn.disabled = false;
            }
        });
    }

    // Вспомогательная функция валидации email
    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Простая функция кастомных уведомлений (Toast)
    function showToast(message, type = 'success') {
        // Проверяем, есть ли уже контейнер для тостов, если нет — создаем
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.classList.add('toast-container');
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.classList.add('toast-item', type);
        toast.textContent = message;

        container.appendChild(toast);

        // Плавное появление и исчезновение
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});
