document.addEventListener('DOMContentLoaded', () => {
    const testsList = document.getElementById('testsList');
    const testContainer = document.getElementById('testContainer');
    const testTitleElement = document.getElementById('testTitle');
    const testForm = document.getElementById('testForm');
    const questionsContainer = document.getElementById('questionsContainer');

    // Получение списка тестов
    fetch('/cyberpolygon/api/tests/')
        .then((response) => response.json())
        .then((data) => {
            if (data.tests && Array.isArray(data.tests)) {
                data.tests.forEach((test) => {
                    const li = document.createElement('li');
                    li.classList.add('list-group-item');
                    li.textContent = test.title;
                    li.dataset.testTitle = test.title; // Добавляем data-атрибут с названием теста
                    testsList.appendChild(li);
                });
            }
        })
        .catch((error) => console.error('Ошибка:', error));

    // Загрузка теста
    testsList.addEventListener('click', (event) => {
        const selectedTestTitle = event.target.dataset.testTitle;

        fetch(`/cyberpolygon/api/tests/?title=${selectedTestTitle}`)
            .then((response) => response.json())
            .then((data) => {
                if (!data || !data.title) {
                    console.error('Ошибка: данные о тесте отсутствуют.');
                    return;
                }

                // Показать контейнер с тестом
                testContainer.style.display = 'block';
                testsList.style.display = 'none';

                // Установить заголовок и описание
                testTitleElement.textContent = data.title;

                // Отображение вопросов и ответов
                questionsContainer.innerHTML = '';
                Object.entries(data.questions).forEach(([questionId, questionData]) => {
                    const questionDiv = document.createElement('div');
                    questionDiv.classList.add('mb-4');
                    questionDiv.innerHTML = `
                        <h5>${questionData.question_text}</h5>
                        ${Object.entries(questionData.answers)
                            .map(
                                ([answerId, answerText]) => `
                                    <div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="question_${questionId}" value="${answerId}">
                                        <label class="form-check-label">${answerText}</label>
                                    </div>`
                            )
                            .join('')}
                    `;
                    questionsContainer.appendChild(questionDiv);
                });
            })
            .catch((error) => console.error('Ошибка:', error));
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
            .then((response) => response.json())
            .then((data) => {
                alert('Результаты: ' + JSON.stringify(data.result));
                window.location.reload();
            })
            .catch((error) => console.error('Ошибка:', error));
    });
});
