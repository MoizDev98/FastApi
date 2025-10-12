<div class="items">
    <input id="search_input" onkeyup="search_func()" type="text" placeholder="search...">
	<ul id="search_items">
		% for item in md:
		<li><a href="/{{item.pretty_filename}}">{{item.url_path}}</a></li>
		% end 
	</ul>
</div>
<div class="markdown-body">
<script src="https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.js"></script>
<textarea id="demo2"># This one autosaves!
By default, it saves every 10 seconds, but this can be changed. When this textarea is included in a form, it will automatically forget the saved value when the form is submitted.</textarea>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/latest/css/font-awesome.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.css">
<script src="https://cdn.jsdelivr.net/simplemde/latest/simplemde.min.js"></script>
<script>
	new SimpleMDE({
		element: document.getElementById("demo2"),
		spellChecker: false,
		autosave: {
			enabled: true,
			unique_id: "demo2",
		},
        value: "Hello chump",
	});
</script>
</div>
