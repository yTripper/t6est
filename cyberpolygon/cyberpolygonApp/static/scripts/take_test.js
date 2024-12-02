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
                testsList.innerHTML = '<p>Нет доступных тестов.</p>';
                return;
            }

            data.tests.forEach((test) => {
                const li = document.createElement('li');
                li.classList.add('list-group-item', 'cursor-pointer');
                li.textContent = test.title;
                li.dataset.testTitle = test.title;
                testsList.appendChild(li);
            });
        })
        .catch((error) => {
            console.error('Ошибка:', error);
            testsList.innerHTML = '<p>Ошибка загрузки списка тестов.</p>';
        });

    // Выбор теста
    testsList.addEventListener('click', (event) => {
        const selectedTestTitle = event.target.dataset.testTitle;
        if (!selectedTestTitle) return;

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
                    questionsContainer.innerHTML = '<p>В этом тесте нет вопросов.</p>';
                    return;
                }

                Object.entries(data.questions).forEach(([questionId, questionData]) => {
                    const questionDiv = document.createElement('div');
                    questionDiv.classList.add('mb-4');

                    const questionTitle = document.createElement('h5');
                    questionTitle.textContent = questionData.question_text;
                    questionDiv.appendChild(questionTitle);

                    questionData.answers.forEach((answer) => {
                        const answerDiv = document.createElement('div');
                        answerDiv.classList.add('form-check');

                        const input = document.createElement('input');
                        input.classList.add('form-check-input');
                        input.type = 'checkbox';
                        input.name = `question_${questionId}`;
                        input.value = answer.id;

                        const label = document.createElement('label');
                        label.classList.add('form-check-label');
                        label.textContent = answer.text;

                        answerDiv.appendChild(input);
                        answerDiv.appendChild(label);
                        questionDiv.appendChild(answerDiv);
                    });

                    questionsContainer.appendChild(questionDiv);
                });
            })
            .catch((error) => {
                console.error('Ошибка:', error);
                testContainer.innerHTML = '<p>Ошибка загрузки данных теста.</p>';
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

        fetch('/cyberpolygon/api/tests/check/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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
