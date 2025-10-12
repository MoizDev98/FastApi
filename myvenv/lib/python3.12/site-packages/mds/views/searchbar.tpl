<div class="search_items">
	<div id="search_input_box">
		<input id="search_input" onkeyup="search_func()" type="text" placeholder="search...">
	</div>

	<ul id="search_items">
		% for item in md:
		<li><a class="note" href="/{{item.pretty_filename}}">{{item.url_path}}</a></li>
		% end 
	</ul>
</div>
