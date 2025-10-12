function search_func() {
  // Declare variables
  var input, filter, ul, li, button, a, i, txtValue;
  input = document.getElementById('search_input');
  filter = input.value.toUpperCase();
  ul = document.getElementById("search_items");
  li = ul.getElementsByTagName('li');
  button = document.getElementsByTagName('button');
  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < li.length; i++) {
    a = li[i].getElementsByTagName("a")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
    // button[0].style.display="none";
  }
}
