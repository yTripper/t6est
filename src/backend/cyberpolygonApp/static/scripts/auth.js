// Кастомные алерты

function showCustomAlert(message, type = 'error') {
    const alertElement = document.getElementById("customAlert");
    const messageElement = document.getElementById("customAlertMessage");

    if (type === 'success') {
        alertElement.style.backgroundColor = '#d4edda';
        alertElement.style.color = '#155724';
        alertElement.style.borderColor = '#c3e6cb';
    } else {
        alertElement.style.backgroundColor = '#f8d7da';
        alertElement.style.color = '#721c24';
        alertElement.style.borderColor = '#f5c6cb';
    }

    messageElement.textContent = message;
    alertElement.classList.remove("d-none");

    setTimeout(() => {
        alertElement.classList.add("d-none");
    }, 3000); // скрываем алерт через 3 секунды
}

function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    return csrfToken;
}

// Очистка полей при открытии модального окна для регистрации
document.getElementById("registrationModal").addEventListener('show.bs.modal', () => {
    document.getElementById("id_username").value = '';
    document.getElementById("id_email").value = '';
    document.getElementById("id_password1").value = '';
    document.getElementById("id_password2").value = '';
});

// Очистка полей при открытии модального окна для входа
document.getElementById("loginModal").addEventListener('show.bs.modal', () => {
    document.getElementById("id_username").value = '';
    document.getElementById("id_password").value = '';
});

document.querySelector("#registrationModal form").addEventListener("submit", (event) => {
    event.preventDefault();

    const username = document.getElementById("id_username_register").value;
    const email = document.getElementById("id_email").value;
    const password = document.getElementById("id_password1").value;
    const confirmPassword = document.getElementById("id_password2").value;

    if (password !== confirmPassword) {
        showCustomAlert("Пароли не совпадают!", 'error');
        return;
    }

    const csrfToken = getCSRFToken();

    // Отправляем данные на сервер
    fetch('/cyberpolygon/api/auth/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Добавляем CSRF токен в заголовок
        },
        body: JSON.stringify({ username, email, password1: password, password2: confirmPassword })
    })
        .then(response => response.json())
        .then(data => {
            console.log("Ответ сервера:", data);

            // Проверяем, успешна ли регистрация
            if (Object.keys(data).length === 0) { // Если объект пустой, считаем регистрацию успешной
                showCustomAlert("Регистрация успешна!", 'success');

                // Закрываем модальное окно после успешной регистрации
                const modalElement = document.getElementById("registrationModal");
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) modal.hide();
            } else {
                // Обрабатываем ошибки, если они есть
                const errorMessage = data.email?.[0] || data.username?.[0] || "Ошибка регистрации. Пожалуйста, проверьте данные.";
                showCustomAlert(errorMessage, 'error');
            }
        })
        .catch(error => {
            showCustomAlert("Ошибка при регистрации. Проверьте подключение к серверу.", 'error');
            console.error("Ошибка при регистрации:", error);
        })
});



function closeModal(modalId) {
  const modalElement = document.getElementById(modalId);
  const modal = bootstrap.Modal.getInstance(modalElement);
  modal.hide();
}



//document.querySelector("#resetPasswordModal form").addEventListener("submit", (event) => {
//  event.preventDefault();

//  const email = document.getElementById("id_email").value;

//  // Отправляем запрос на сервер для восстановления пароля
//    fetch('/cyberpolygon/api/reset-password', {
//    method: 'POST',
//    headers: {
//      'Content-Type': 'application/json'
//    },
//    body: JSON.stringify({ email })
//  })
//    .then(response => response.json())
//    .then(data => {
//      if (data.success) {
//        showCustomAlert("Инструкции по восстановлению пароля отправлены на ваш email.", 'success');
//      } else {
//        showCustomAlert("Пользователь с таким email не найден.", 'error');
//      }
//    })
//    .catch(error => {
//      showCustomAlert("Ошибка при восстановлении пароля.", 'error');
//      console.error(error);
//    });
//});




document.getElementById("showPassword").addEventListener("change", (event) => {
  const passwordInput = document.getElementById("id_password");
  if (event.target.checked) {
      passwordInput.type = "text";
  } else {
      passwordInput.type = "password";
  }
});

// Функция для проверки, вошел ли пользователь
function checkLoggedInUser() {
    const loggedInUser = localStorage.getItem('loggedInUser');
    const loginLink = document.getElementById('loginLink');
    const profileLink = document.getElementById('profileLink');
    const logoutLink = document.getElementById('logoutLink');

    if (loggedInUser) {
        const user = JSON.parse(loggedInUser);
        // Скрываем кнопку "Войти"
        loginLink.style.display = 'none';

        // Показываем ссылку на профиль и кнопку "Выйти"
        profileLink.style.display = 'block';
        logoutLink.style.display = 'block';

        // Устанавливаем имя пользователя в профиле
        document.getElementById('usernameDisplay').textContent = user.username;
    } else {
        // Если нет пользователя, показываем "Войти"
        loginLink.style.display = 'block';
        profileLink.style.display = 'none';
        logoutLink.style.display = 'none';
    }
}

// Вызов функции при загрузке страницы
document.addEventListener('DOMContentLoaded', checkLoggedInUser);


// Логика для выхода
document.getElementById('logoutButton').addEventListener('click', function () {
    // Удаляем информацию о пользователе из localStorage
    localStorage.removeItem('loggedInUser');
    showCustomAlert("Вы вышли из системы.", 'error');

    // Обновляем отображение навигации
    checkLoggedInUser();

    // Перенаправляем на главную страницу
    window.location.href = homeUrl;
});


document.addEventListener('DOMContentLoaded', function () {
    // Функция для проверки, вошел ли пользователь
    function checkLoggedInUser() {
        const loggedInUser = localStorage.getItem('loggedInUser');
        const loginLink = document.getElementById('loginLink');
        const profileDropdown = document.getElementById('profileDropdown');
        const usernameDisplay = document.getElementById('usernameDisplay');

        if (loggedInUser) {
            const user = JSON.parse(loggedInUser);
            // Скрываем кнопку "Войти"
            loginLink.style.display = 'none';

            // Показываем выпадающий список профиля
            profileDropdown.style.display = 'block';

            // Устанавливаем имя пользователя в выпадающем списке
            usernameDisplay.textContent = user.username;
        } else {
            // Если нет пользователя, показываем "Войти"
            loginLink.style.display = 'block';
            profileDropdown.style.display = 'none';
        }
    }

    // Проверяем статус пользователя при загрузке страницы
    checkLoggedInUser();

    // Обрабатываем событие входа
document.querySelector("#loginModal form").addEventListener("submit", (event) => {
    event.preventDefault();

    const username = document.getElementById("id_username_login").value;
    const password = document.getElementById("id_password").value;

    // Получаем CSRF токен из cookie
    const csrfToken = getCSRFToken();

    // Отправляем данные на сервер для авторизации
    fetch('/cyberpolygon/api/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Убедитесь, что csrfToken передается
        },
        credentials: 'include',
        body: JSON.stringify({ username, password }) // Здесь только username и password
    })
        .then(response => response.json().then(data => ({ status: response.status, body: data})))
            .then(({ status, body }) => {
                console.log("Ответ сервера:", body);
                if (status === 200) {
                    showCustomAlert("Успешная авторизация!", 'success');
                // Закрываем модальное окно
                    localStorage.setItem('loggedInUser', JSON.stringify({ username })); // Сохраняем информацию о пользователе
                    const modalElement = document.getElementById("loginModal");
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) modal.hide();
                    window.location.reload();
            } else {
                    const errorMessage = body.detail || "Ошибка вхожа. Проверьте введенные данные.";
                    showCustomAlert(errorMessage, 'error');
            }
        })
        .catch(error => {
            showCustomAlert("Ошибка при входе. Проверьте подключение к серверу.", 'error');
            console.error("Ошибка при входе:", error);
        });
});



    // Логика для выхода
    document.getElementById('logoutButton').addEventListener('click', function () {
        // Удаляем информацию о пользователе из localStorage
        localStorage.removeItem('loggedInUser');
        showCustomAlert("Вы вышли из системы.", 'error');

        // Обновляем отображение навигации
        checkLoggedInUser();

        // Перенаправляем на главную страницу
        window.location.href = homeUrl;
    });
});






// Функция для проверки, вошел ли пользователь перед переходом на страницу
function checkUserAndRedirect(event) {
    const loggedInUser = localStorage.getItem('loggedInUser');

    if (!loggedInUser) {
        // Блокируем переход по ссылке
        event.preventDefault();
        // Выводим алерт о необходимости войти в аккаунт
        showCustomAlert('Пожалуйста, войдите в аккаунт, чтобы читать больше.', 'error');
    }
}

// Получаем элемент кнопки по ID и добавляем обработчик клика
const readMoreBtn = document.getElementById('readMoreBtn');
readMoreBtn.addEventListener('click', checkUserAndRedirect);


// Мдам

