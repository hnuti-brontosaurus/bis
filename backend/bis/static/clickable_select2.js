document.addEventListener("click", function(event){
    if (event.target.className === 'select2-selection__choice') {
        $el = event.target
        index = Array.from($el.parentNode.querySelectorAll('.select2-selection__choice')).indexOf($el)
        select = $el.parentElement.parentElement.parentElement.parentElement.parentElement.querySelector('select')

        id = select.querySelectorAll('option')[index].value
        window.open('/admin/bis/user/' + id + '/change/')
        event.stopPropagation()
        event.preventDefault()
    }
});
