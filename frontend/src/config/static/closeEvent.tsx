export const form = {
  photos: {
    help: 'Nahraj 5-30 reprezentativních fotek z akce, které budou ukazovat účastníky při dobrovolnické práci a zobrazovat další program akce.',
  },
  record: {
    total_hours_worked: {
      help: 'Napište kolik hodin strávili všichni účastníci a organizátoři dobrovolnickou prací. Např.: Na akci se dva dny kosila louka. Každý den se pracovalo 6 hodin a pracovalo 10 účastníků a 2 organizátoři. Všichni tedy dobrovolnickou prací strávili 2 dny x 6 hodin x 12 lidí =  144 člověkohodin.',
    },
  },
  feedback_form: {
    introduction: {
      initial:
        'Ahoj,\n\ndoufáme, že sis víkendovku nebo tábor užil*a naplno, poznal*a nové lidi a odvezl*a si fajn zážitky i zkušenosti.\n' +
        'Budeme moc rádi, když nám teď věnuješ pár minut a dáš nám vědět, jaké to pro tebe bylo. Tvoje zpětná vazba nám pomáhá dělat akce ještě lepší.',
      help: 'Text, který se objeví na začátku dotazníku. Pokud chceš, můžeš si připravený text opravit.',
    },
    after_submit_text: {
      initial:
        'Moc děkujeme za vyplnění a těšíme se na viděnou na další akci Hnutí Brontosaurus!\nTvoji organizátoři a ústředí Hnutí Brontosaurus.',
      help: 'Tento text dojde účastníkům po vyplnění zpětné vazby. Doporučujeme jako odměnu přidat např. odkaz na fotky z akce, adresář či jiné drobnosti.',
    },
    email_subject: {
      initial: 'Jaký to bylo? Zpětná vazba z akce',
    },
    email_content: {
      initial: `
        <p>Ahoj *|vokativ|*,</p>
        <p>&hellip; doufáme, že se po *|event_name|* cítíš jenom dobře! 😊</p>
        <p><br></p>
        <p> A teď upřímně — <b>jaký to bylo?</b></p>
        <p>Když připravujeme akce, vždycky se opíráme hlavně o to, co nám napíšete do zpětné vazby.</p>
        <p><i>Podle ní ladíme program, atmosféru i to, co má na akcích opravdu smysl.</i></p>
        <p><br></p>
        <p>Takže&hellip; jestli nám můžeš věnovat pár minut, moc nám to pomůže. 🙏💚</p>
      `,
    },
  },
}
