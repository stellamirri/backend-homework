document.addEventListener("DOMContentLoaded", () => {  
  console.log("connecting to the SocketIO backend");

  const socket = io(); 

  socket.on('connect', () => {
    console.log('Connected!');
    socket.emit('connect-ack', { messages: `I\m connected!` });
  });

  socket.on('note_updated', (data) => {display_new_message(data);});

  const display_new_message = (data) => {
    const { id, done } = data;
    const checkbox = document.querySelector(`input[data-id="${id}"]`);
    if (checkbox) {
      checkbox.checked = done;
    }
  };

  // document.querySelectorAll('input[type="checkbox"]:checked').forEach(box => {
  //   box.checked = false;
  // });

  document.querySelectorAll(".note>form>input").forEach((element) => {
    element.addEventListener("change", (event) => {
      const done = element.checked;
      const id = element.dataset.id;

      fetch(`/api/notes/${id}/done`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ done }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.ok) {
            console.log("ok");
          } else {
            console.log("update failed", data);
          }
        })
        .catch((error) => {
          console.error("Fetch error:", error);
        });
    });
  });
})
