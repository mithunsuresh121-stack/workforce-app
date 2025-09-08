const inputBox = document.getElementById("input-box");
const listContainer = document.getElementById("list-container");
const taskCount = document.getElementById("task-count");
const clearCompletedBtn = document.getElementById("clear-completed");

function addTask() {
    if (inputBox.value === '') {
        alert("You must write something!");
    } else {
        let li = document.createElement("li");
        li.innerHTML = inputBox.value;
        let span = document.createElement("span");
        span.innerHTML = "\u00d7";
        li.appendChild(span);
        listContainer.appendChild(li);
    }
    inputBox.value = "";
    saveData();
    updateTaskCount();
}

listContainer.addEventListener("click", function(e) {
    if (e.target.tagName === "LI") {
        e.target.classList.toggle("checked");
        saveData();
        updateTaskCount();
    } else if (e.target.tagName === "SPAN") {
        e.target.parentElement.remove();
        saveData();
        updateTaskCount();
    }
}, false);

function saveData() {
    let tasks = [];
    listContainer.querySelectorAll("li").forEach(li => {
        tasks.push({
            text: li.innerText.slice(0, -1), // remove the ×
            checked: li.classList.contains("checked")
        });
    });
    localStorage.setItem("tasks", JSON.stringify(tasks));
}

function showTask() {
    let tasks = JSON.parse(localStorage.getItem("tasks")) || [];
    tasks.forEach(task => {
        let li = document.createElement("li");
        li.innerHTML = task.text;
        let span = document.createElement("span");
        span.innerHTML = "\u00d7";
        li.appendChild(span);
        if (task.checked) {
            li.classList.add("checked");
        }
        listContainer.appendChild(li);
    });
    updateTaskCount();
}

function updateTaskCount() {
    let total = listContainer.querySelectorAll("li").length;
    let completed = listContainer.querySelectorAll("li.checked").length;
    taskCount.innerText = `${total} tasks (${completed} completed)`;
}

function clearCompleted() {
    listContainer.querySelectorAll("li.checked").forEach(li => li.remove());
    saveData();
    updateTaskCount();
}

clearCompletedBtn.addEventListener("click", clearCompleted);

inputBox.addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        addTask();
    }
});

showTask();
