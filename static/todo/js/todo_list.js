document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.btn-todo-complete').forEach(button => {
        button.addEventListener('click', function (e) {
            e.stopPropagation();

            const todoCard = this.closest('.todo-card');
            const todoList = todoCard.closest('.todos-list');
            const todoId = todoCard.dataset.id;
            const icon = this.querySelector('i');
            const isCompleted = todoCard.classList.toggle('completed');

            if (isCompleted) {
                icon.classList.remove('bi-circle');
                icon.classList.add('bi-check-circle-fill');
            } else {
                icon.classList.remove('bi-check-circle-fill');
                icon.classList.add('bi-circle');
            }

            fetch(`/todo/${todoId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN
                },
                body: JSON.stringify({
                    completed: isCompleted
                })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to update todo');
                    }

                    console.log(`Todo ${todoId} updated`);

                    if (isCompleted) {
                        todoList.appendChild(todoCard);
                    } else {
                        const firstCompleted = todoList.querySelector('.todo-card.completed');

                        if (firstCompleted) {
                            todoList.insertBefore(todoCard, firstCompleted);
                        } else {
                            todoList.appendChild(todoCard);
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);

                    todoCard.classList.toggle('completed');

                    if (isCompleted) {
                        icon.classList.remove('bi-check-circle-fill');
                        icon.classList.add('bi-circle');
                    } else {
                        icon.classList.remove('bi-circle');
                        icon.classList.add('bi-check-circle-fill');
                    }
                });
        });
    });
});
