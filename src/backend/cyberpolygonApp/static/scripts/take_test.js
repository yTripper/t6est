document.addEventListener('DOMContentLoaded', () => {
    const testsList = document.getElementById('testsList');
    const testContainer = document.getElementById('testContainer');
    const testTitleElement = document.getElementById('testTitle');
    const testDescriptionElement = document.getElementById('testDescription');
    const questionsContainer = document.getElementById('questionsContainer');
    const testForm = document.getElementById('testForm');
    const backButton = document.getElementById('backButton');

    // Загрузка списка тестов
    fetch('/cyberpolygon/api/tests/')
        .then((response) => {
            if (!response.ok) throw new Error(`Ошибка загрузки тестов: ${response.statusText}`);
            return response.json();
        })
        .then((data) => {
            if (!data.tests || data.tests.length === 0) {
                testsList.innerHTML = '<div class="alert alert-info">Нет доступных тестов.</div>';
                return;
            }

            const row = document.createElement('div');
            row.classList.add('row', 'g-4');

            data.tests.forEach((test) => {
                const col = document.createElement('div');
                col.classList.add('col-md-6', 'col-lg-4');

                const card = document.createElement('div');
                card.classList.add('card', 'h-100', 'shadow-sm', 'test-card');
                card.innerHTML = `
                    <div class="card-body">
                        <h5 class="card-title">${test.title}</h5>
                        <p class="card-text text-muted">${test.description || 'Описание отсутствует'}</p>
                        <button class="btn btn-primary start-test-btn" data-test-title="${test.title}">
                            Начать тест
                        </button>
                    </div>
                `;

                col.appendChild(card);
                row.appendChild(col);
            });

            testsList.appendChild(row);
        })
        .catch((error) => {
            console.error('Ошибка:', error);
            testsList.innerHTML = '<div class="alert alert-danger">Ошибка загрузки списка тестов.</div>';
        });

    // Выбор теста
    testsList.addEventListener('click', (event) => {
        const startButton = event.target.closest('.start-test-btn');
        if (!startButton) return;

        const selectedTestTitle = startButton.dataset.testTitle;

        fetch(`/cyberpolygon/api/tests/?title=${encodeURIComponent(selectedTestTitle)}`)
            .then((response) => {
                if (!response.ok) throw new Error(`Ошибка загрузки теста: ${response.statusText}`);
                return response.json();
            })
            .then((data) => {
                testsList.style.display = 'none';
                testContainer.style.display = 'block';

                testTitleElement.textContent = data.title || 'Без названия';
                testDescriptionElement.textContent = data.description || 'Описание отсутствует';

                questionsContainer.innerHTML = '';

                if (!data.questions || Object.keys(data.questions).length === 0) {
                    questionsContainer.innerHTML = '<div class="alert alert-info">В этом тесте нет вопросов.</div>';
                    return;
                }

                Object.entries(data.questions).forEach(([questionId, questionData], index) => {
                    const questionDiv = document.createElement('div');
                    questionDiv.classList.add('card', 'mb-4', 'shadow-sm');

                    const questionContent = document.createElement('div');
                    questionContent.classList.add('card-body');

                    const questionHeader = document.createElement('h5');
                    questionHeader.classList.add('card-title', 'mb-4');
                    questionHeader.textContent = `Вопрос ${index + 1}: ${questionData.question_text}`;

                    const answersDiv = document.createElement('div');
                    answersDiv.classList.add('answers-container');

                    questionData.answers.forEach((answer) => {
                        const answerDiv = document.createElement('div');
                        answerDiv.classList.add('form-check', 'custom-answer', 'mb-3');

                        const input = document.createElement('input');
                        input.classList.add('form-check-input');
                        input.type = 'checkbox';
                        input.name = `question_${questionId}`;
                        input.value = answer.id;
                        input.id = `answer_${answer.id}`;

                        const label = document.createElement('label');
                        label.classList.add('form-check-label');
                        label.htmlFor = `answer_${answer.id}`;
                        label.textContent = answer.text;

                        answerDiv.appendChild(input);
                        answerDiv.appendChild(label);
                        answersDiv.appendChild(answerDiv);
                    });

                    questionContent.appendChild(questionHeader);
                    questionContent.appendChild(answersDiv);
                    questionDiv.appendChild(questionContent);
                    questionsContainer.appendChild(questionDiv);
                });
            })
            .catch((error) => {
                console.error('Ошибка:', error);
                testContainer.innerHTML = '<div class="alert alert-danger">Ошибка загрузки данных теста.</div>';
            });
    });

    // Отправка ответов
    testForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const answers = {};
        questionsContainer.querySelectorAll('input:checked').forEach((input) => {
            const questionId = input.name.split('_')[1];
            if (!answers[questionId]) answers[questionId] = [];
            answers[questionId].push(input.value);
        });

        // Получаем CSRF токен
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/cyberpolygon/api/tests/check/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken // Добавляем CSRF токен в заголовки
            },
            credentials: 'include', // Важно для работы с сессиями
            body: JSON.stringify({ title: testTitleElement.textContent, questions: answers }),
        })
            .then((response) => {
                if (!response.ok) throw new Error(`Ошибка отправки ответов: ${response.statusText}`);
                return response.json();
            })
            .then((data) => {
                if (!data.result) {
                    alert('Ошибка обработки результата.');
                    return;
                }
            
                const resultSummary = Object.entries(data.result).map(([questionId, details]) => {
                    const { correct, submitted_answers, correct_answers } = details;
            
                    const questionResult = correct
                        ? `Вопрос ${questionId}: Правильно`
                        : `Вопрос ${questionId}: Неправильно\nВаш ответ: ${submitted_answers.join(', ')}\nПравильный ответ: ${correct_answers.join(', ')}`;
            
                    return questionResult;
                }).join('\n');
            
                alert(`Результаты:\n${resultSummary}`);
                window.location.reload();
            })            
            .catch((error) => {
                console.error('Ошибка:', error);
                alert('Ошибка отправки ответов.');
            });
    });

    // Кнопка "Назад"
    backButton.addEventListener('click', () => {
        testContainer.style.display = 'none';
        testsList.style.display = 'block';
    });
});
