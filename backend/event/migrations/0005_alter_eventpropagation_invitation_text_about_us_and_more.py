# Generated by Django 4.0.10 on 2023-03-05 07:45

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_eventregistration_alternative_registration_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventpropagation',
            name='invitation_text_about_us',
            field=tinymce.models.HTMLField(blank=True, help_text='Malá ochutnávka uvádí fotky, které k akci přiložíte. Popište fotky, které přikládáte nebo přibližte jak vypadaly akce na stejném místě v minulosti. U nových akcí můžete více ukázat místo a důvody proč vás oslovilo a představit organizátory.'),
        ),
        migrations.AlterField(
            model_name='eventpropagation',
            name='invitation_text_introduction',
            field=tinymce.models.HTMLField(help_text='Základní informace o tvé akci. Popiš téma akce a nastiň, co se tam bude dít a jak budete pomáhat, co se účastník naučí nového. Prvních několik vět se zobrazí v přehledu akcí na webu. První věty jsou k upoutání pozornosti nejdůležitější, proto se na ně zaměř a shrň ve 2-4 větách na co se účastníci mohou těšit.'),
        ),
        migrations.AlterField(
            model_name='eventpropagation',
            name='invitation_text_practical_information',
            field=tinymce.models.HTMLField(help_text='Stručný popis programu akce – jakého typu budou aktivity na akci, kde se bude spát, co se bude jíst a další praktické záležitosti. Nezapomeň zdůraznit, zda bude program aktivní a plný zážitkového programu nebo bude spíše poklidnější nebo zaměřený na vzdělávání. Také napiš zda bude program fyzicky popř. psychicky náročný, aby účastníci věděli co mají čekat.'),
        ),
        migrations.AlterField(
            model_name='eventpropagation',
            name='invitation_text_work_description',
            field=tinymce.models.HTMLField(blank=True, help_text='Stručně popiš dobrovolnickou činnost a její smysl pro přírodu, památky nebo lidi (např. „sázíme vrbky, aby měli místní ptáci kde hnízdit“). Zasaď dobrovolnickou pomoc do kontextu místa a jeho příběhu (např. “kosením pomůžeme udržet pestrost nejvzácnější louky unikátní krajiny Bílých Karpat, jež …” ). Napiš, co se při práci účastníci naučí a v čem je to může rozvinout. Přidej i další zajímavosti, které se vážou k dané dobrovolnické činnosti a lokalitě. Uveď kolik prostoru na akci se bude věnovat dobrovolnické činnosti a jak bude náročná.'),
        ),
    ]