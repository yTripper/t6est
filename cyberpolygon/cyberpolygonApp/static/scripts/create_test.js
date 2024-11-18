document.addEventListener('DOMContentLoaded', () => {
    const createTestForm = document.getElementById('createTestForm');
    const addQuestionButton = document.getElementById('addQuestionButton');
    const questionsContainer = document.getElementById('questionsContainer');

    let questionCount = 0;

    // Функция для добавления нового вопроса
    addQuestionButton.addEventListener('click', () => {
        questionCount++;
        const questionDiv = document.createElement('div');
        questionDiv.classList.add('mb-3');
        questionDiv.innerHTML = `
            <label for="question_${questionCount}" class="form-label">Вопрос ${questionCount}</label>
            <input type="text" class="form-control" id="question_${questionCount}" required>
            <div id="answers_${questionCount}" class="mt-2"></div>
            <button type="button" class="btn btn-sm btn-secondary mt-2 add-answer" data-question="${questionCount}">Добавить ответ</button>
        `;
        questionsContainer.appendChild(questionDiv);
    });

    // Добавление ответа к вопросу
    questionsContainer.addEventListener('click', (event) => {
        if (event.target.classList.contains('add-answer')) {
            const questionId = event.target.dataset.question;
            const answersDiv = document.getElementById(`answers_${questionId}`);
            const answerCount = answersDiv.childElementCount + 1;

            const answerDiv = document.createElement('div');
            answerDiv.classList.add('input-group', 'mb-2');
            answerDiv.innerHTML = `
                <input type="text" class="form-control" placeholder="Ответ ${answerCount}" required>
                <div class="input-group-text">
                    <input type="checkbox" class="form-check-input" title="Правильный ответ">
                </div>
            `;
            answersDiv.appendChild(answerDiv);
        }
    });
    function getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        return csrfToken;
    }
    createTestForm.addEventListener('submit', async (event) => {
        event.preventDefault();
    
        const testTitle = document.getElementById('testTitle').value.trim();
        const testDescription = document.getElementById('testDescription').value.trim(); 
        const csrfToken = getCSRFToken();
        const currenttimestamp = new Date().toISOString();
        
        try {
            // Создаем тест
            const testResponse = await fetch('/cyberpolygon/api/tests/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json', 
                    'X-CSRFToken': csrfToken // Добавляем CSRF-токен
                },
                body: JSON.stringify({ 
                    title: testTitle, 
                    description: testDescription,
                }),
            });
    
            // Проверка ответа сервера
            const responseData = await testResponse.json();
            if (!testResponse.ok) {
                console.error('Ошибка создания теста:', responseData);
                alert('Ошибка создания теста: ' + (responseData.detail || 'Неизвестная ошибка'));
                return;
            }
    
            alert('Тест успешно создан!');
            createTestForm.reset();
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Ошибка создания теста. Проверьте подключение к серверу.');
        }
    });
    
    
});
