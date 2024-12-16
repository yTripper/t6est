let correctAnswers = 0; // Переменная для подсчета правильных ответов
let totalQuestions = 6; // Общее количество вопросов

function checkAnswer(button, isCorrect, explanation) {
    const explanationText = button.parentNode.querySelector('.explanation');
    explanationText.innerText = explanation;
    explanationText.style.display = 'block';

    if (isCorrect) {
        button.classList.remove('btn-primary');
        button.classList.add('btn-success');
        explanationText.style.color = 'green'; // Зелёный для правильного ответа
        correctAnswers++; // Увеличиваем счётчик правильных ответов
    } else {
        button.classList.remove('btn-primary');
        button.classList.add('btn-danger');
        explanationText.style.color = 'red'; // Красный для неправильного ответа
    }

    // Блокируем все кнопки после выбора
    const buttons = button.parentNode.querySelectorAll('button');
    buttons.forEach(btn => btn.disabled = true);

    // Обновляем результат на экране
    updateResult();
}

function updateResult() {
    const resultText = document.getElementById('result');
    resultText.innerText = `Правильные ответы: ${correctAnswers} из ${totalQuestions}`;
}

