document.addEventListener('DOMContentLoaded', () => {
    const profileForm = document.getElementById('profileForm');
    const usernameInput = document.getElementById('id_username');
    const tg_profileInput = document.getElementById('id_tg_profile');
    const avatarInput = document.getElementById('id_avatar');
    const cardAvatar = document.getElementById('cardAvatar');
    const formMessage = document.getElementById('formMessage');

    const cardUsername = document.getElementById('cardUsername');
    const cardTg = document.getElementById('cardTg');

    let initialUsername = usernameInput ? usernameInput.value.trim() : '';
    let initialTGProfile = tg_profileInput ? tg_profileInput.value.trim() : '';
    let isAvatarChanged = false;

    if (!profileForm) return;

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Смена Username
    async function changeUsername(username) {
        const response = await fetch('/profile/change-username/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ username: username })
        });

        const data = await response.json();

        if (!response.ok) {
            const errorMsg = Object.entries(data)
                .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
                .join('; ');
            throw new Error(errorMsg || 'Не удалось изменить username.');
        }
        return data;
    }

    // Смена TGProfile
    async function changeTGProfile(tg_profile_username) {
        const response = await fetch('/api/tg-profile/current/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ telegram_username: tg_profile_username })
        });

        const data = await response.json();

        if (!response.ok) {
            const errorMsg = Object.entries(data)
                .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
                .join('; ');
            throw new Error(errorMsg || 'Не удалось изменить tg_profile.');
        }
        return data;
    }

    // смена Avatar
    async function changeAvatar(fileObject) {
        const formData = new FormData();
        formData.append('avatar', fileObject);

        // Поменяйте этот урл на ваш реальный эндпоинт для загрузки картинок
        const response = await fetch('/profile/change-avatar/', {
            method: 'PATCH',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            const errorMsg = Object.entries(data)
                .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
                .join('; ');
            throw new Error(errorMsg || 'Не удалось обновить аватар.');
        }
        return data;
    }

    // Превью аватара
    if (avatarInput && cardAvatar) {
        avatarInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                if (file.size > 2 * 1024 * 1024) {
                    showMessage('Файл слишком большой. Максимум 2 МБ.', 'error');
                    this.value = '';
                    isAvatarChanged = false;
                    return;
                }

                isAvatarChanged = true;
                const reader = new FileReader();
                reader.onload = function(e) {
                    cardAvatar.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // ОТПРАВКА ФОРМЫ
    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const currentUsername = usernameInput ? usernameInput.value.trim() : '';
        const currentTGProfile = tg_profileInput ? tg_profileInput.value.trim() : '';

        const isUsernameChanged = currentUsername !== initialUsername;
        const isTGProfileChanged = currentTGProfile !== initialTGProfile;

        if (isUsernameChanged && currentUsername.length < 3) {
            showMessage('Имя пользователя должно быть не короче 3 символов.', 'error');
            return;
        }

        showMessage('Сохранение...', 'info');

        try {
            if (isUsernameChanged) {
                const usernameData = await changeUsername(currentUsername);
                if (usernameData.username && cardUsername) {
                    cardUsername.textContent = usernameData.username;
                }
                initialUsername = currentUsername;
            }

            if (isTGProfileChanged) {
                const tgData = await changeTGProfile(currentTGProfile);
                if (cardTg) {
                    const tgValue = tgData.telegram_username || tgData.tg_profile;
                    cardTg.textContent = tgValue ? `@${tgValue}` : 'Не указан';
                }
                initialTGProfile = currentTGProfile;
            }

            if (isAvatarChanged && avatarInput.files[0]) {
                const avatarData = await changeAvatar(avatarInput.files[0]);
                if (avatarData.avatar && cardAvatar) {
                    cardAvatar.src = avatarData.avatar + '?t=' + new Date().getTime();
                }
                isAvatarChanged = false;
            }

            showMessage('Изменения успешно сохранены!', 'success');

        } catch (error) {
            console.error('Error:', error);
            showMessage(error.message || 'Ошибка при сохранении данных.', 'error');
        }
    });

    function showMessage(text, type) {
        if (!formMessage) return;
        formMessage.textContent = text;
        formMessage.className = 'form-message';

        if (type === 'success') {
            formMessage.classList.add('msg-success');
            formMessage.style.color = '#2ec4b6';
        } else if (type === 'error') {
            formMessage.classList.add('msg-error');
            formMessage.style.color = '#e71d36';
        } else {
            formMessage.style.color = '#888';
        }
    }
});
