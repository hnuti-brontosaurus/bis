function focus() {
	document.getElementById('focus').focus();
}

function confirm_delete() {
	return confirm('Opravdu chcete vymazat tuto položku z databáze?');
}

function confirm_remove() {
	return confirm('Opravdu chcete tohoto člena odstranit ze seznamu (v BISu jeho adresa zůstane)?');
}

function confirm_remove_mm() {
	return confirm('Opravdu chcete tohoto člena odstranit za celé uvedené období (v BISu jeho adresa zůstane)?');
}

function showpopup($id) {
      document.getElementById($id).style.visibility = 'visible';
}

function hidepopup($id) {
      document.getElementById($id).style.visibility = 'hidden';
}
