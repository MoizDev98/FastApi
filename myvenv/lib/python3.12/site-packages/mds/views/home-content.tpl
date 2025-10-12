	<ul id="search_items">
		% for item in md:
		<li><a class="note" href="/{{item.pretty_filename}}">{{item.url_path}}</a></li>
		% end 
	</ul>