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
            <input type="text" class="form-control question-text" id="question_${questionCount}" required>
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
                <input type="text" class="form-control answer-text" placeholder="Ответ ${answerCount}" required>
                <div class="input-group-text">
                    <input type="checkbox" class="form-check-input correct-answer" title="Правильный ответ">
                </div>
            `;
            answersDiv.appendChild(answerDiv);
        }
    });

    // Получение CSRF токена
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Обработка отправки формы
    createTestForm.addEventListener('submit', async (event) => {
        event.preventDefault();
    
        const testTitle = document.getElementById('testTitle').value.trim();
        const testDescription = document.getElementById('testDescription').value.trim();
        const csrfToken = getCSRFToken();
    
        // Сбор вопросов и ответов
        const questions = [];

        questionsContainer.querySelectorAll('.mb-3').forEach((questionDiv, questionIndex) => {
            const questionText = questionDiv.querySelector('.question-text').value.trim();
            const answers = [];
        
            questionDiv.querySelectorAll('.input-group').forEach((answerDiv) => {
                const answerText = answerDiv.querySelector('.answer-text').value.trim();
                const isCorrect = answerDiv.querySelector('.correct-answer').checked;
        
                answers.push({
                    answer_text: answerText,
                    is_correct: isCorrect,
                });
            });
        
            questions.push({
                question_text: questionText,
                answers: answers,
            });
        });
        
        console.log('Сформированные данные для отправки:', questions);
        console.log('Данные для отправки на сервер:', JSON.stringify({
            title: testTitle,
            description: testDescription,
            questions: questions,
        }, null, 2));
        
    
        try {
            // Шаг 1: Создание теста
            const testResponse = await fetch('/cyberpolygon/api/tests/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    title: testTitle,
                    description: testDescription,
                }),
            });
        
            if (!testResponse.ok) {
                const errorData = await testResponse.json();
                console.error('Ошибка создания теста:', errorData);
                alert('Ошибка создания теста: ' + (errorData.detail || 'Неизвестная ошибка'));
                return;
            }
        
            // Шаг 2: Добавление вопросов
            const contentResponse = await fetch('/cyberpolygon/api/tests/content/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    title: testTitle,
                    questions: questions, // Отправляем массив вопросов
                }),
            });
            
        
            if (!contentResponse.ok) {
                const errorData = await contentResponse.json();
                console.error('Ошибка добавления вопросов:', errorData);
                alert('Ошибка добавления вопросов: ' + (errorData.detail || 'Неизвестная ошибка'));
                return;
            }
        
            alert('Тест успешно сохранен!');
            createTestForm.reset();
            questionsContainer.innerHTML = '';
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Ошибка сохранения. Проверьте подключение к серверу.');
        }
    });
});