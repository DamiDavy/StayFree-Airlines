document.addEventListener('DOMContentLoaded', function () {

    //show departure and arrival cities after form submition
    const departure = document.querySelector('#depatures_input').value;
    const arrival = document.querySelector('#arrivals_input').value;
    if (!departure && !arrival) {
        document.querySelector('#ahead-titles').style.display = "none";
    }
    else {
        document.querySelector('#ahead-titles').style.display = "block";
        document.querySelector('#ahead-titles').innerHTML = departure + " - " + arrival;
    }

    if (document.querySelector('#round-trip').checked === true) {
        document.querySelector('#back-titles').innerHTML = arrival + " - " + departure;
    }

    //adding min attribute equal today to date field
    let now = new Date();
    let day = ("0" + now.getDate()).slice(-2);
    let month = ("0" + (now.getMonth() + 1)).slice(-2);
    let today = now.getFullYear() + "-" + (month) + "-" + (day);
    let earliest = document.createAttribute("min");
    earliest.value = today;
    document.querySelector('#date').setAttributeNode(earliest);
    if (document.querySelector('#date').value === "") {
        document.querySelector('#date').value = today;
    }

    //one-way(round trip) checkbox depends on return date input 
    if (document.querySelector('#back').value == "") {
        document.querySelector('#round-trip').checked = false;
        document.querySelector('#one-way').checked = true;
    }
    else {
        document.querySelector('#round-trip').checked = true;
        document.querySelector('#one-way').checked = false;
    }

    document.querySelector('#back').addEventListener("change", () => {
        if (document.querySelector('#back').value == "") {
            document.querySelector('#round-trip').checked = false;
            document.querySelector('#one-way').checked = true;
        }
        else {
            document.querySelector('#round-trip').checked = true;
            document.querySelector('#one-way').checked = false;
        }
    })

    if (document.querySelector('#trans').innerHTML == "['transfer']")
        document.querySelector('#transfer').checked = true;
    else
        document.querySelector('#transfer').checked = false;

    //added variables for some inputs and search results
    const depatures_input = document.querySelector('#depatures_input');
    const arrivals_input = document.querySelector('#arrivals_input');

    const depatures_block = document.querySelector('#depatures');
    const arrivals_block = document.querySelector('#arrivals');

    //loading search results when typing in departure or destination city
    depatures_input.addEventListener("keyup", () => {
        if (depatures_input.value != "")
            load_search('depatures');
        else
            depatures_block.style.display = "none";
    })

    arrivals_input.addEventListener("keyup", () => {
        if (arrivals_input.value != "")
            load_search('arrivals');
        else
            arrivals_block.style.display = "none";
    })

    //make search results disappear when clicking 
    document.querySelector('body').addEventListener('click', () => {
        depatures_block.style.display = "none";
        arrivals_block.style.display = "none";
    })

    //exchanging values of departure and destination cities
    document.querySelector('#exchange').addEventListener("click", () => {
        let c = arrivals_input.value;
        arrivals_input.value = depatures_input.value;
        depatures_input.value = c;
    })

    //return date can't be earlier then date of departure
    document.querySelector('#back').addEventListener("click", () => {
        let d = document.querySelector('#date').value;
        let back = document.querySelector('#back');
        let earl = document.createAttribute("min");
        earl.value = d;
        back.setAttributeNode(earl);
    })

    //show input for date of return
    document.querySelector('#round-trip').addEventListener("change", () => {
        const back = document.querySelector('#back');
        if (document.querySelector('#round-trip:checked')) {
            back.disabled = false;
            document.querySelector('#one-way').checked = false;
        }
        else {
            back.disabled = true;
            back.value;
        }
    })

    document.querySelector('#one-way').addEventListener("change", () => {
        const back = document.querySelector('#back');
        if (document.querySelector('#one-way:checked')) {
            document.querySelector('#round-trip').checked = false;
            back.disabled = true;
            back.value = "";
        }
        else
            back.disabled = false;
    })

    //initially search blocks are not visible
    depatures_block.style.display = "none";
    arrivals_block.style.display = "none";
})


//searching of cities in dababase starts with input value
function load_search(what) {
    const res = document.querySelector(`#${what}`);
    res.style.display = 'block';
    const pattern = document.querySelector(`#${what}_input`).value;
    fetch("/search", {
        method: 'POST',
        body: JSON.stringify({
            pattern: pattern
        })
    })
        .then(response => response.json())
        .then(results => {
            //if no results
            if (results == "") {
                res.style.display = "none";
            }
            else {
                res.innerHTML = "";
                results.forEach(item => {
                    const element = document.createElement("span");
                    element.innerHTML = item["city"];
                    element.classList.add("city-item");
                    res.append(element);
                    //set input value
                    element.addEventListener('click', () => {
                        document.querySelector(`#${what}_input`).value = element.innerHTML;
                        res.style.display = "none";
                    })
                })
            }
        })
}