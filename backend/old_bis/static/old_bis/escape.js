// The frontend skips its 1 April redirect to the old BIS while this key
// holds the current year, see frontend/src/utils/redirectToOldBis.ts
function escape_to_new_bis() {
	localStorage.setItem('old-bis-escaped', new Date().getFullYear());
	location.href = '/';
	return false;
}
