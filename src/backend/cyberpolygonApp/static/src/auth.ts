const dbName: string = "UserAuthDB";
const dbVersion: number = 1;
let db: IDBDatabase | null = null;

// Открытие или создание базы данных
const request: IDBOpenDBRequest = indexedDB.open(dbName, dbVersion);

request.onerror = (event: Event) => {
    console.log("Ошибка при работе с базой данных", event);
};

request.onsuccess = (event: Event) => {
    db = (event.target as IDBOpenDBRequest).result;
    console.log("База данных успешно открыта");
};

request.onupgradeneeded = (event: IDBVersionChangeEvent) => {
    db = (event.target as IDBOpenDBRequest).result;
    if (db && !db.objectStoreNames.contains("users")) {
        const userStore = db.createObjectStore("users", { keyPath: "email" });
        userStore.createIndex("email", "email", { unique: true });
    }
};

document.querySelector("#registrationModal form")?.addEventListener("submit", (event: Event) => {
    event.preventDefault();

    const username = (document.getElementById("username") as HTMLInputElement).value;
    const email = (document.getElementById("registerEmail") as HTMLInputElement).value;
    const password = (document.getElementById("registerPassword") as HTMLInputElement).value;
    const confirmPassword = (document.getElementById("confirmPassword") as HTMLInputElement).value;

    if (password !== confirmPassword) {
        alert("Пароли не совпадают!");
        return;
    }

    if (db) {
        const transaction = db.transaction(["users"], "readwrite");
        const userStore = transaction.objectStore("users");

        const user = { username, email, password };

        const request = userStore.add(user);

        request.onsuccess = () => {
            alert("Регистрация успешна!");
        };

        request.onerror = () => {
            alert("Пользователь с таким email уже зарегистрирован.");
        };
    }
});

document.querySelector("#loginModal form")?.addEventListener("submit", (event: Event) => {
    event.preventDefault();

    const email = (document.getElementById("email") as HTMLInputElement).value;
    const password = (document.getElementById("password") as HTMLInputElement).value;

    if (db) {
        const transaction = db.transaction(["users"], "readonly");
        const userStore = transaction.objectStore("users");
        const request = userStore.get(email);

        request.onsuccess = (event: Event) => {
            const user = (event.target as IDBRequest).result;
            if (user && user.password === password) {
                alert("Вход успешен!");

                // Переход на страницу личного кабинета
                setTimeout(function () {
                    closeModal('loginModal'); // Закрытие модального окна
                    window.location.href = 'personal_account.html';
                }, 1000);

            } else {
                alert("Неверный email или пароль.");
            }
        };

        request.onerror = () => {
            alert("Ошибка при входе.");
        };
    }
});

function closeModal(modalId: string): void {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        modal?.hide();
    }
}

document.querySelector("#resetPasswordModal form")?.addEventListener("submit", (event: Event) => {
    event.preventDefault();

    const email = (document.getElementById("resetEmail") as HTMLInputElement).value;

    if (db) {
        const transaction = db.transaction(["users"], "readonly");
        const userStore = transaction.objectStore("users");
        const request = userStore.get(email);

        request.onsuccess = (event: Event) => {
            const user = (event.target as IDBRequest).result;
            if (user) {
                // Здесь можно отправить email с инструкциями или показать пароль
                alert(`Ваш пароль: ${user.password}`);
            } else {
                alert("Пользователь с таким email не найден.");
            }
        };

        request.onerror = () => {
            alert("Ошибка при восстановлении пароля.");
        };
    }
});

document.getElementById("showPassword")?.addEventListener("change", (event: Event) => {
    const passwordInput = document.getElementById("password") as HTMLInputElement;
    const target = event.target as HTMLInputElement;
    if (target.checked) {
        passwordInput.type = "text";
    } else {
        passwordInput.type = "password";
    }
});
