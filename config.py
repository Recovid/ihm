mesure = dict(
	ratio_width = 0.009,
	color_text_sync ='black',
	color_text_unsync ='dark slate gray',
	background = "#edf0f6",
	background_alarmOn = '#ff2026',
	font_family = "Helvetica",
	font_ratio_value = 0.4,
	font_ratio_value_frac = 0.35,
	font_ratio_title = 0.09,
	font_ratio_unit = 0.09,
	height_ratio_unit = 0.19,
)

alarmValue = dict(
	width_ratio = 0.3,
	height_ratio = 0.25,
	unit_value = 0.1,
	color_text ='black',
	background = "#edf0f6",
	background_selected = "red",
	font_family = "Helvetica",
)

knob = dict(
	width = 100,
	height = 130,
	font_family = "Helvetica",
	font_ratio_value = 0.2,
	font_ratio_unit = 0.1,
	font_ratio_title = 0.12,
	font_ratio_unit_frac = 0.08,
	color_arc = "#4E69AB",
	background = "grey",
	background_selected = "#c9d2e5",
	color_text_sync ='white',
	color_text_unsync ='dark slate gray',
) 

button = dict(
	width_ratio = 1,
	height_ratio = 1,
	font_family = "Helvetica bold",
	font_ratio_value = 0.1,
        font = ("Helvetica bold", 10),
        font_big = ("Helvetica bold", 15),
	background = "#c9d2e5",
	btn_background = "grey",
	btn_background_selected = "#c9d2e5",
	color_text ='white',
)
lockScreen = dict(
        font_timer=("Helvetica bold", 100),
        font_title=("Helvetica bold", 30),
)
powerSettings = dict(
        bg_quit = 'red',
        bg_lock = 'yellow',
        font = ("Helvetica bold", 20),
        fg = 'black',
)

valueDialog = dict(
	width = 300,
	height = 250,
	font_family = "Helvetica",
	font_size_value = 40,
	font_size_input = 20,

)

minMaxDialog = dict(
	width = 300,
	height = 250,
	font_family = "Helvetica",
	font_size = 30,
)

newPatientDialog = dict(
	width = 300,
	height = 250,
	font_family = "Helvetica",
	font_size_size = 20,
	font_size_button = 20,

)

batteryDisplay = dict(
	yellow_thresh = 85,
)

titleDialog = dict(
	width = 400,
	height = 300,
	ref_technique = "Référence Technique du produit: \n completer la ref",
	ihm_version = "V2.0.0",
	ctrl_version = "V2.0.0",
	fab = "Société MinMaxMedical \n Zone Mayencin II - Parc Equation - Bâtiment 1\n 2 Avenue de Vignate \n 38610 Gières - France",
	inst_util = "Instruction Utilisateur",
)
