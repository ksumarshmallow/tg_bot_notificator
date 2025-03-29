import React, { useState, useEffect } from "react";
import axios from "axios";
import { useLocation } from "react-router-dom";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";

const Calendar = () => {
  const location = useLocation();
  const userId = new URLSearchParams(location.search).get("user_id");

  const [events, setEvents] = useState([]);
  const backendUrl = "http://127.0.0.1:5001"; 

  // Загружаем события с бэка
  useEffect(() => {
    const userId = 1; // TODO: получить ID пользователя из контекста
    axios
      .get(`${backendUrl}/events?user_id=${userId}`)
      .then((response) => setEvents(response.data))
      .catch((error) => console.error("Error loading events", error));
  }, []);

  // Функция для добавления события
  const addEvent = (date) => {
    const eventName = prompt("Введите название события");
    const userId = 1;
    if (eventName) {
      axios
        .post(`${backendUrl}/events`, {
          user_id: userId,
          name: eventName,
          date: date,
        })
        .then((response) => {
          setEvents([...events, response.data]); // обновляем события
        })
        .catch((error) => console.error("Error adding event", error));
    }
  };

  // Функция для редактирования события
  const editEvent = (event) => {
    const updatedName = prompt("Измените название события", event.title);
    const userId = 1;
    if (updatedName) {
      axios
        .put(`${backendUrl}/events/${event.id}`, {
          name: updatedName,
        })
        .then((response) => {
          const updatedEvents = events.map((e) =>
            e.id === event.id ? { ...e, title: updatedName } : e
          );
          setEvents(updatedEvents);
        })
        .catch((error) => console.error("Error updating event", error));
    }
  };

  // Функция для удаления события
  const deleteEvent = (event) => {
    if (window.confirm("Вы уверены, что хотите удалить это событие?")) {
      const userId = 1;
      axios
        .post(`${backendUrl}/events/delete`, {
          user_id: userId,
          name: event.title,
          date: event.startStr, // TODO: передать startStr как дату
        })
        .then(() => {
          setEvents(events.filter((e) => e.id !== event.id));
        })
        .catch((error) => console.error("Error deleting event", error));
    }
  };

  return (
    <div>
      <FullCalendar
        plugins={[dayGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        events={events}
        dateClick={(info) => addEvent(info.dateStr)} // Добавление события по клику
        eventClick={(info) => {
          const action = prompt(
            "Выберите действие: 1 - редактировать, 2 - удалить"
          );
          if (action === "1") {
            editEvent(info.event);
          } else if (action === "2") {
            deleteEvent(info.event);
          }
        }}
      />
    </div>
  );
};

export default Calendar;