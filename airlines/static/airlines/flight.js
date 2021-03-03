document.addEventListener('DOMContentLoaded', function () {

    const single_price = document.querySelector('#single_price').innerHTML;
    const pas_count = document.querySelector('#pas_count').innerHTML;
    const price_for_transit = document.querySelector('#price_for_transit').innerHTML;

    let baggage_price;
    let pas_bag_count;

    if (document.querySelector('#baggage_price') && document.querySelector('#pas_bag_count')) {
        baggage_price = document.querySelector('#baggage_price').innerHTML;
        pas_bag_count = document.querySelector('#pas_bag_count').innerHTML;
    }
    else {
        baggage_price = 0
        pas_bag_count = 0
    }

    let trans;

    if (price_for_transit === "")
        trans = 0;
    else
        trans = price_for_transit;

    document.querySelector('#total_price').innerHTML = ((1 * pas_count) * ((1 * single_price) + (1 * trans))) +
        (1 * baggage_price * pas_bag_count);
})