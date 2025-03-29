async function getEventsByDate(date) {
    const userId = localStorage.getItem("user_id");
    const response = await fetch(`/events/by_date?user_id=${userId}&date=${date}`);
    const data = await response.json();
    return data.events; // Возвращает список событий
}

// Инициализация календаря
const calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
    plugins: ['dayGrid'],
    initialView: 'dayGridMonth',
    locale: 'ru',
    events: async function(info, successCallback) {
        const events = await getEventsByDate(info.startStr);
        successCallback(events);
    }
});

calendar.render();
