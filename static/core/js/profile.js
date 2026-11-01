document.addEventListener('DOMContentLoaded', () => {
    const profileForm = document.getElementById('profileForm');
    const avatarInput = document.getElementById('id_avatar');
    const cardAvatar = document.getElementById('cardAvatar');
    const formMessage = document.getElementById('formMessage');

    const cardUsername = document.getElementById('cardUsername');
    const cardEmail = document.getElementById('cardEmail');
    const cardTg = document.getElementById('cardTg');

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

    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(profileForm);

        if (!isAvatarChanged) {
            formData.delete('avatar');
        }

        showMessage('Сохранение...', 'info');

        try {
            const response = await fetch('/api/tg-profile/current/', {
                method: 'PATCH',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('Изменения успешно сохранены!', 'success');

                if (data.username && cardUsername) cardUsername.textContent = data.username;
                if (data.email && cardEmail) cardEmail.textContent = data.email;

                if (cardTg) {
                    if (data.tg_profile) {
                        cardTg.textContent = `@${data.tg_profile}`;
                    } else {
                        cardTg.textContent = 'Не указан';
                    }
                }

                if (data.avatar && cardAvatar) {
                    cardAvatar.src = data.avatar;
                }
            } else {
                let errorMsg = 'Ошибка при сохранении: ';
                if (typeof data === 'object') {
                    errorMsg += Object.entries(data)
                        .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
                        .join('; ');
                } else {
                    errorMsg += 'Что-то пошло не так.';
                }
                showMessage(errorMsg, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('Ошибка сети. Не удалось связаться с сервером.', 'error');
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
