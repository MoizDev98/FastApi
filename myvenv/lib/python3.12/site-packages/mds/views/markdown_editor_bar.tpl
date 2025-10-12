<div id="midbar">
    <div class="buttons">
    <button onclick="window.location.href='../{{f.pretty_filename}}'">Back</button>
    <button onclick="saveFile('{{ f.absolute_path }}')">Save</button>
    <button onclick="deleteFile('{{ f.absolute_path }}')">Delete</button>
</div>
<h5>{{f.pretty_filename}}</h5>
</div>
