const countdown = document.querySelectorAll('#countDown');
countdown.forEach(function (el) {
    var date = el.getAttribute('data-date');
    const dateParts = date.split(' '); // Split the string into an array of parts

    // Create a new Date object using the parts
    date = new Date(dateParts[2], dateParts[1] - 1, dateParts[0], dateParts[3], dateParts[4]);
    const countDownDate = new Date(date).getTime();
    const x = setInterval(function () {
        const now = new Date().getTime();
        const distance = countDownDate - now;
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        el.querySelector('#days').innerText = days + " Days";
        el.querySelector('#hours').innerText = hours + " Hours";
        el.querySelector('#minutes').innerText = minutes + " Minutes";
        el.querySelector('#seconds').innerText = seconds + " Seconds";

        if (distance < 0) {
            clearInterval(x);
            el.innerHTML = "EXPIRED";
        }
    }, 1000);
});