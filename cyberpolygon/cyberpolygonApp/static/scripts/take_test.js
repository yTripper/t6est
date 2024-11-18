document.addEventListener('DOMContentLoaded', () => {
    const testsList = document.getElementById('testsList');
    const testContainer = document.getElementById('testContainer');
    const testTitle = document.getElementById('testTitle');
    const testForm = document.getElementById('testForm');
    const questionsContainer = document.getElementById('questionsContainer');

    // Получение списка тестов
    fetch('/cyberpolygon/api/tests/')
        .then((response) => response.json())
        .then((data) => {
            data.tests.forEach((test) => {
                const li = document.createElement('li');
                li.classList.add('list-group-item');
                li.textContent = test.title;
                li.dataset.testTitle = test.title;
                testsList.appendChild(li);
            });
        })
        .catch((error) => console.error('Ошибка:', error));

    // Загрузка теста
    testsList.addEventListener('click', (event) => {
        const testTitle = event.target.dataset.testTitle;

        fetch(`/cyberpolygon/api/tests/?title=${testTitle}`)
            .then((response) => response.json())
            .then((data) => {
                testContainer.style.display = 'block';
                testsList.style.display = 'none';

                testTitle.textContent = data.title;
                questionsContainer.innerHTML = '';

                Object.keys(data.questions).forEach((questionId) => {
                    const question = data.questions[questionId];
                    const questionDiv = document.createElement('div');
                    questionDiv.classList.add('mb-4');
                    questionDiv.innerHTML = `
                        <h5>${question[0]}</h5>
                        ${Object.keys(question[1])
                            .map(
                                (answerId) =>
                                    `<div class="form-check">
                                        <input class="form-check-input" type="checkbox" name="question_${questionId}" value="${answerId}">
                                        <label class="form-check-label">${question[1][answerId]}</label>
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
            body: JSON.stringify({ title: testTitle.textContent, questions: answers }),
        })
            .then((response) => response.json())
            .then((data) => {
                alert('Результаты: ' + JSON.stringify(data.result));
                window.location.reload();
            })
            .catch((error) => console.error('Ошибка:', error));
    });
});
