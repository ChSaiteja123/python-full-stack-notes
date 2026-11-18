(() => {
  "use strict";

  const stateKey = "python-full-stack-academy-v1";
  const status = document.querySelector("#app-status");
  const content = document.querySelector("#course-content");
  const monthFilter = document.querySelector("#month-filter");
  const searchInput = document.querySelector("#lesson-search");
  const bookmarksOnly = document.querySelector("#bookmarks-only");
  const notesInput = document.querySelector("#lesson-notes");
  const selectedLesson = document.querySelector("#selected-lesson");
  const storage = {
    available: true,
    load() {
      try {
        const raw = window.localStorage.getItem(stateKey);
        if (!raw) return { completed: [], bookmarks: [], notes: {}, selectedDay: null };
        const parsed = JSON.parse(raw);
        if (!parsed || !Array.isArray(parsed.completed) || !Array.isArray(parsed.bookmarks) || !parsed.notes || typeof parsed.notes !== "object" || Array.isArray(parsed.notes)) {
          throw new TypeError("Saved course data has an unexpected shape.");
        }
        return { ...parsed, selectedDay: Number.isInteger(parsed.selectedDay) ? parsed.selectedDay : null };
      } catch (error) {
        this.available = false;
        status.textContent = `Progress could not be loaded from browser storage: ${error.message}`;
        status.classList.add("error");
        return { completed: [], bookmarks: [], notes: {}, selectedDay: null };
      }
    },
    save(value) {
      if (!this.available) return;
      try {
        window.localStorage.setItem(stateKey, JSON.stringify(value));
      } catch (error) {
        this.available = false;
        status.textContent = `Progress could not be saved to browser storage: ${error.message}`;
        status.classList.add("error");
      }
    },
  };
  let state = storage.load();
  let lessons = [];
  let months = [];

  function showStatus(message, isError = false) {
    if (status.classList.contains("error") && !isError) return;
    status.textContent = message;
    status.classList.toggle("error", isError);
  }

  function persist() {
    storage.save(state);
    updateProgress();
  }

  function updateProgress() {
    const completed = new Set(state.completed);
    const count = lessons.filter((lesson) => completed.has(lesson.day)).length;
    const percent = lessons.length ? Math.round((count / lessons.length) * 100) : 0;
    document.querySelector("#progress-summary").textContent = `${count} of ${lessons.length} lessons complete · ${percent}%`;
    document.querySelector("#progress-bar").style.width = `${percent}%`;
    document.querySelector(".progress-track").setAttribute("aria-valuenow", String(count));
  }

  function makeButton(label, action, day, secondary = false) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.dataset.action = action;
    button.dataset.day = String(day);
    if (secondary) button.classList.add("secondary");
    return button;
  }

  function selectLesson(lesson) {
    state.selectedDay = lesson.day;
    selectedLesson.textContent = `Notes for Day ${String(lesson.day).padStart(3, "0")}: ${lesson.title}`;
    notesInput.value = state.notes[String(lesson.day)] || "";
  }

  function render() {
    content.replaceChildren();
    const query = searchInput.value.trim().toLowerCase();
    const monthValue = monthFilter.value;
    const savedBookmarks = new Set(state.bookmarks);
    let visibleCount = 0;

    for (const month of months) {
      if (monthValue !== "all" && Number(monthValue) !== month.number) continue;
      const monthLessons = month.lessons.filter((lesson) => {
        const matchesSearch = `${lesson.title} ${month.name} ${lesson.day}`.toLowerCase().includes(query);
        const matchesBookmark = !bookmarksOnly.checked || savedBookmarks.has(lesson.day);
        return matchesSearch && matchesBookmark;
      });
      if (!monthLessons.length) continue;
      visibleCount += monthLessons.length;

      const section = document.createElement("section");
      section.className = "month-card";
      const header = document.createElement("header");
      const heading = document.createElement("h2");
      heading.textContent = `Month ${month.number}: ${month.name}`;
      const focus = document.createElement("p");
      focus.textContent = month.focus;
      header.append(heading, focus);
      const list = document.createElement("ul");
      list.className = "lesson-list";

      for (const lesson of monthLessons) {
        const item = document.createElement("li");
        const completed = state.completed.includes(lesson.day);
        item.className = `lesson-card${completed ? " is-complete" : ""}`;
        const day = document.createElement("span");
        day.className = "lesson-day";
        day.textContent = `DAY ${String(lesson.day).padStart(3, "0")}`;
        const link = document.createElement("a");
        link.className = "lesson-title";
        link.href = lesson.html;
        link.textContent = lesson.title;
        link.addEventListener("focus", () => selectLesson(lesson));
        link.addEventListener("click", () => selectLesson(lesson));
        const actions = document.createElement("div");
        actions.className = "lesson-actions";
        actions.append(
          makeButton(completed ? "Mark incomplete" : "Mark complete", "complete", lesson.day, true),
          makeButton(savedBookmarks.has(lesson.day) ? "Remove bookmark" : "Bookmark", "bookmark", lesson.day, true),
        );
        item.append(day, link, actions);
        list.append(item);
      }
      section.append(header, list);
      content.append(section);
    }

    if (!visibleCount) {
      const empty = document.createElement("p");
      empty.className = "empty-state panel";
      empty.textContent = "No lessons match these filters.";
      content.append(empty);
    }
    updateProgress();
  }

  content.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const day = Number(button.dataset.day);
    if (button.dataset.action === "complete") {
      state.completed = state.completed.includes(day)
        ? state.completed.filter((item) => item !== day)
        : [...state.completed, day];
      persist();
      render();
    } else if (button.dataset.action === "bookmark") {
      state.bookmarks = state.bookmarks.includes(day)
        ? state.bookmarks.filter((item) => item !== day)
        : [...state.bookmarks, day];
      persist();
      render();
    }
  });

  document.querySelector("#save-note").addEventListener("click", () => {
    if (!Number.isInteger(state.selectedDay)) {
      showStatus("Choose a lesson before saving a note.");
      return;
    }
    state.notes[String(state.selectedDay)] = notesInput.value;
    persist();
    showStatus("Note saved in this browser.");
  });

  searchInput.addEventListener("input", render);
  monthFilter.addEventListener("change", render);
  bookmarksOnly.addEventListener("change", render);

  fetch("course-index.json")
    .then((response) => {
      if (!response.ok) throw new Error(`Course catalog request failed with HTTP ${response.status}.`);
      return response.json();
    })
    .then((data) => {
      if (!Array.isArray(data.months) || data.months.length !== 6) {
        throw new TypeError("Course catalog must contain six months.");
      }
      months = data.months;
      lessons = months.flatMap((month) => month.lessons);
      for (const month of months) {
        const option = document.createElement("option");
        option.value = String(month.number);
        option.textContent = `Month ${month.number}: ${month.name}`;
        monthFilter.append(option);
      }
      render();
      const initialLesson = lessons.find((lesson) => lesson.day === state.selectedDay);
      if (initialLesson) selectLesson(initialLesson);
      showStatus("Course catalog loaded. Progress and bookmarks are stored locally in this browser.");
    })
    .catch((error) => {
      showStatus(`Dashboard could not load the course catalog: ${error.message}`, true);
    });
})();
