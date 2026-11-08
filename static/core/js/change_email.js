document.addEventListener('DOMContentLoaded', () => {
    // EMAIL MODAL
    const emailModal = document.getElementById('emailModal');
    const emailEditBtn = document.getElementById('emailEditBtn');
    const closeEmailModal = document.getElementById('closeEmailModal');
    const newEmailInput = document.getElementById('newEmail');
    const changeEmailBtn = document.getElementById('changeEmailBtn');
    const emailError = document.getElementById('emailError');

    // CODE MODAL
    const codeModal = document.getElementById('codeModal');
    const closeCodeModal = document.getElementById('closeCodeModal');
    const verificationCode = document.getElementById('verificationCode');
    const submitCodeBtn = document.getElementById('submitCodeBtn');
    const codeError = document.getElementById('codeError');

    // EMAIL ELEMENTS
    const cardEmail = document.getElementById('cardEmail');
    const emailDisplayValue = document.getElementById('emailDisplayValue');

    if (!emailModal || !emailEditBtn || !closeEmailModal) return;

    // CSRF TOKEN
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrfToken = getCookie('csrftoken');

    // MODAL FUNCTIONS
    function openEmailModal() {
        emailModal.classList.add('active');
        newEmailInput.value = '';
        emailError.textContent = '';
        setTimeout(() => newEmailInput.focus(), 100);
    }

    function openCodeModal() {
        codeModal.classList.add('active');
        verificationCode.value = '';
        codeError.textContent = '';
        setTimeout(() => verificationCode.focus(), 100);
    }

    function closeAllModals() {
        emailModal.classList.remove('active');
        if (codeModal) codeModal.classList.remove('active');
    }

    // OPEN / CLOSE EVENTS
    emailEditBtn.addEventListener('click', openEmailModal);
    closeEmailModal.addEventListener('click', closeAllModals);
    if (closeCodeModal) closeCodeModal.addEventListener('click', closeAllModals);

    emailModal.addEventListener('click', (e) => {
        if (e.target === emailModal) closeAllModals();
    });

    if (codeModal) {
        codeModal.addEventListener('click', (e) => {
            if (e.target === codeModal) closeAllModals();
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeAllModals();
    });

    // CHANGE EMAIL REQUEST
    if (changeEmailBtn) {
        changeEmailBtn.addEventListener('click', async () => {
            const newEmail = newEmailInput.value.trim().toLowerCase();

            if (!newEmail) {
                emailError.textContent = 'Введите новый email.';
                return;
            }

            if (!newEmailInput.checkValidity()) {
                emailError.textContent = 'Введите корректный email.';
                return;
            }

            emailError.textContent = '';
            changeEmailBtn.disabled = true;
            changeEmailBtn.textContent = 'Sending...';

            try {
                const response = await fetch('/accounts/change-email/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ email: newEmail })
                });

                const data = await response.json();

                if (!response.ok) {
                    emailError.textContent = data.error || 'Произошла ошибка.';
                    return; // Блок finally отработает автоматически
                }

                closeAllModals();
                openCodeModal();
            } catch (error) {
                emailError.textContent = 'Ошибка соединения с сервером.';
                console.error(error);
            } finally {
                changeEmailBtn.disabled = false;
                changeEmailBtn.textContent = 'Change';
            }
        });
    }

    // VERIFY EMAIL CODE
    if (submitCodeBtn) {
        submitCodeBtn.addEventListener('click', async () => {
            const code = verificationCode.value.trim();

            if (!/^\d{6}$/.test(code)) {
                codeError.textContent = 'Введите корректный 6-значный код.';
                return;
            }

            codeError.textContent = '';
            submitCodeBtn.disabled = true;
            submitCodeBtn.textContent = 'Checking...';

            try {
                const response = await fetch('/accounts/verify-email-change/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ code: code })
                });

                const data = await response.json();

                if (!response.ok) {
                    codeError.textContent = data.error || 'Неверный код.';
                    return;
                }

                // Обновляем email на странице из ответа бэкенда
                if (cardEmail && data.email) cardEmail.textContent = data.email;
                if (emailDisplayValue && data.email) emailDisplayValue.textContent = data.email;

                closeAllModals();
                alert(data.message || 'Email успешно изменён!');
            } catch (error) {
                codeError.textContent = 'Ошибка соединения с сервером.';
                console.error(error);
            } finally {
                submitCodeBtn.disabled = false;
                submitCodeBtn.textContent = 'Submit';
            }
        });
    }
});
