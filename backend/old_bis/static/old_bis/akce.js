function poc() {
	var pocet = 0;
	var pocet_start = 0;
	var form = document.forms[0];

	pocet += form.tabor_nazev.value.length;
	pocet += form.tabor_od.value.length;
	pocet += form.tabor_do.value.length;
	pocet += form.tabor_vek_od.value.length;
	pocet_start += (form.tabor_vek_od.value.length > 0 ? 8 : 0);
	pocet += form.tabor_poplatek.value.length;
	pocet += form.tabor_kontakt_email.value.length;
	pocet += form.tabor_web.value.length;

	/* combobox lokalita */
	sel = form.tabor_lokalita.selectedIndex;
	if (sel != null) {
		pocet += form.tabor_lokalita[sel].text.length;
	}

	pocet += form.tabor_lokalita_jina.value.length;
	pocet += form.tabor_text_kratsi.value.length;

	form.chars.value = pocet + pocet_start;
}


function toggle_required(form, prefix, required, fields) {
	for (var i = 0; i < fields.length; i++) {
		spans = form[prefix + fields[i]].parentNode.getElementsByTagName('span');
		spans[0].style.visibility = required ? 'visible' : 'hidden';
	}
}


function akce_toggle() {
	var form = document.forms[0];
	var cbTyp     = form.akce_typ;
	var cbProgram = form.akce_program;
	var cbPrihlaska = form.akce_prihlaska;
	var typ       = cbTyp.options[cbTyp.selectedIndex].value;
	var program   = cbProgram.options[cbProgram.selectedIndex].value;
	var prihlaska = cbPrihlaska.options[cbPrihlaska.selectedIndex].value;

	toggle_required(
		form, 'akce_',
		form.akce_zverejnit.checked,
		['kontakt_telefon', 'kontakt_email', 'text_uvod', 'text_info', 'priloha_1']
	);
	toggle_required(form, 'akce_', typ == 1, ['text_dobr']);
	toggle_required(form, 'akce_', form.akce_zverejnit.checked && prihlaska == 3, ['kontakt_url']);
}


function tabor_toggle() {
	var form      = document.forms[0];
	var cbTyp     = form.tabor_typ;
	var cbProgram = form.tabor_program;
	var cbProkoho = form.tabor_prokoho;
	var cbPrihlaska = form.tabor_prihlaska;
	var typ       = cbTyp.options[cbTyp.selectedIndex].value;
	var program   = cbProgram.options[cbProgram.selectedIndex].value;
	var prokoho   = cbProkoho.options[cbProkoho.selectedIndex].value;
	var prihlaska = cbPrihlaska.options[cbPrihlaska.selectedIndex].value;

	toggle_required(
		form, 'tabor_',
		form.tabor_zverejnit.checked,
		['text_uvod', 'text_info', 'text_kratsi', 'priloha_1']
	);
	toggle_required(
		form, 'tabor_',
		typ == 1 || program == 1 || program == 3,
		['text_dobr', 'pracovni_doba', 'pracovni_dny']
	);
	toggle_required(
		form, 'tabor_',
		program == 3 || program == 4,
		['odpovedna']
	);
	toggle_required(
		form, 'tabor_',
		prokoho == 3 || prokoho == 4,
		['ubytovani', 'strava']
	);
	toggle_required(form, 'tabor_', form.tabor_zverejnit.checked && prihlaska == 3, ['kontakt_url']);

	poc();
}
