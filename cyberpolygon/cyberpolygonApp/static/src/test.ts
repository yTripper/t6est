let correctAnswers: number = 0; // Переменная для подсчета правильных ответов
const totalQuestions: number = 6;

function checkAnswer(button: HTMLButtonElement, isCorrect: boolean, explanation: string): void {
    const explanationText = button.parentElement?.querySelector('.explanation') as HTMLElement;
    if (explanationText) {
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
        const buttons = button.parentElement?.querySelectorAll('button') as NodeListOf<HTMLButtonElement>;
        buttons.forEach(btn => btn.disabled = true);
    
        // Обновляем результат на экране
        updateResult();
    }
}

function updateResult(): void {
    const resultText = document.getElementById('result') as HTMLElement;
    if (resultText) {
        resultText.innerText = `Правильные ответы: ${correctAnswers} из ${totalQuestions}`;
    }
}
