import customtkinter as ctk


class MaterialColors:
    LIGHT_SCHEME = {
        "primary": "#6750A4",
        "on_primary": "#FFFFFF",
        "primary_container": "#EADDFF",
        "on_primary_container": "#21005D",
        "secondary": "#625B71",
        "on_secondary": "#FFFFFF",
        "secondary_container": "#E8DEF8",
        "on_secondary_container": "#1D192B",
        "tertiary": "#7D5260",
        "on_tertiary": "#FFFFFF",
        "tertiary_container": "#FFD8E4",
        "on_tertiary_container": "#31111D",
        "surface": "#FFFBFE",
        "on_surface": "#1C1B1F",
        "surface_variant": "#E7E0EC",
        "on_surface_variant": "#49454F",
        "background": "#FFFBFE",
        "on_background": "#1C1B1F",
        "error": "#B3261E",
        "on_error": "#FFFFFF",
        "error_container": "#F9DEDC",
        "on_error_container": "#410E0B",
        "outline": "#79747E",
        "outline_variant": "#CAC4D0",
        "shadow": "#000000",
        "scrim": "#000000",
        "inverse_surface": "#313033",
        "inverse_on_surface": "#F4EFF4",
        "inverse_primary": "#D0BCFF",
        "surface_tint": "#6750A4",
        "primary_fixed": "#EADDFF",
        "on_primary_fixed": "#21005D",
        "primary_fixed_dim": "#D0BCFF",
        "on_primary_fixed_variant": "#4F378B",
        "secondary_fixed": "#E8DEF8",
        "on_secondary_fixed": "#1D192B",
        "secondary_fixed_dim": "#CCC2DC",
        "on_secondary_fixed_variant": "#4A4458",
        "tertiary_fixed": "#FFD8E4",
        "on_tertiary_fixed": "#31111D",
        "tertiary_fixed_dim": "#EFB8C8",
        "on_tertiary_fixed_variant": "#633B48",
        "surface_dim": "#DED8E1",
        "surface_bright": "#FFFBFE",
        "surface_container_lowest": "#FFFFFF",
        "surface_container_low": "#F7F2FA",
        "surface_container": "#F3EDF7",
        "surface_container_high": "#ECE6F0",
        "surface_container_highest": "#E6E0E9",
    }

    DARK_SCHEME = {
        "primary": "#D0BCFF",
        "on_primary": "#371E73",
        "primary_container": "#4F378B",
        "on_primary_container": "#EADDFF",
        "secondary": "#CCC2DC",
        "on_secondary": "#332D41",
        "secondary_container": "#4A4458",
        "on_secondary_container": "#E8DEF8",
        "tertiary": "#EFB8C8",
        "on_tertiary": "#492532",
        "tertiary_container": "#633B48",
        "on_tertiary_container": "#FFD8E4",
        "surface": "#1C1B1F",
        "on_surface": "#E6E1E5",
        "surface_variant": "#49454F",
        "on_surface_variant": "#CAC4D0",
        "background": "#1C1B1F",
        "on_background": "#E6E1E5",
        "error": "#F2B8B5",
        "on_error": "#601410",
        "error_container": "#8C1D18",
        "on_error_container": "#F9DEDC",
        "outline": "#938F99",
        "outline_variant": "#49454F",
        "shadow": "#000000",
        "scrim": "#000000",
        "inverse_surface": "#E6E1E5",
        "inverse_on_surface": "#313033",
        "inverse_primary": "#6750A4",
        "surface_tint": "#D0BCFF",
        "primary_fixed": "#EADDFF",
        "on_primary_fixed": "#21005D",
        "primary_fixed_dim": "#D0BCFF",
        "on_primary_fixed_variant": "#4F378B",
        "secondary_fixed": "#E8DEF8",
        "on_secondary_fixed": "#1D192B",
        "secondary_fixed_dim": "#CCC2DC",
        "on_secondary_fixed_variant": "#4A4458",
        "tertiary_fixed": "#FFD8E4",
        "on_tertiary_fixed": "#31111D",
        "tertiary_fixed_dim": "#EFB8C8",
        "on_tertiary_fixed_variant": "#633B48",
        "surface_dim": "#141218",
        "surface_bright": "#3B383E",
        "surface_container_lowest": "#0F0D13",
        "surface_container_low": "#1D1B20",
        "surface_container": "#211F26",
        "surface_container_high": "#2B2930",
        "surface_container_highest": "#36343B",
    }

    @classmethod
    def get_color(cls, color_name, dark_mode=False):
        scheme = cls.DARK_SCHEME if dark_mode else cls.LIGHT_SCHEME
        return scheme.get(color_name, "#000000")


class MaterialTypography:
    DISPLAY_LARGE = ("Segoe UI", 57, "normal")
    DISPLAY_MEDIUM = ("Segoe UI", 45, "normal")
    DISPLAY_SMALL = ("Segoe UI", 36, "normal")

    HEADLINE_LARGE = ("Segoe UI", 32, "normal")
    HEADLINE_MEDIUM = ("Segoe UI", 28, "normal")
    HEADLINE_SMALL = ("Segoe UI", 24, "normal")

    TITLE_LARGE = ("Segoe UI", 22, "bold")
    TITLE_MEDIUM = ("Segoe UI", 16, "bold")
    TITLE_SMALL = ("Segoe UI", 14, "bold")

    LABEL_LARGE = ("Segoe UI", 14, "bold")
    LABEL_MEDIUM = ("Segoe UI", 12, "bold")
    LABEL_SMALL = ("Segoe UI", 11, "bold")

    BODY_LARGE = ("Segoe UI", 16, "normal")
    BODY_MEDIUM = ("Segoe UI", 14, "normal")
    BODY_SMALL = ("Segoe UI", 12, "normal")


class MD3Button(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        button_type = kwargs.pop('button_type', 'filled')
        size = kwargs.pop('size', 'medium')

        dark_mode = ctk.get_appearance_mode() == "Dark"

        base_kwargs = {
            'corner_radius': 20 if size == 'medium' else (16 if size == 'small' else 24),
            'border_width': 0,
            'font': MaterialTypography.LABEL_LARGE,
        }

        if button_type == 'filled':
            base_kwargs.update({
                'fg_color': MaterialColors.get_color('primary', dark_mode),
                'hover_color': MaterialColors.get_color('primary_container', dark_mode),
                'text_color': MaterialColors.get_color('on_primary', dark_mode),
            })
        elif button_type == 'outlined':
            base_kwargs.update({
                'fg_color': 'transparent',
                'border_width': 1,
                'border_color': MaterialColors.get_color('outline', dark_mode),
                'text_color': MaterialColors.get_color('primary', dark_mode),
                'hover_color': MaterialColors.get_color('surface_container', dark_mode),
            })
        elif button_type == 'text':
            base_kwargs.update({
                'fg_color': 'transparent',
                'text_color': MaterialColors.get_color('primary', dark_mode),
                'hover_color': MaterialColors.get_color('surface_container', dark_mode),
            })
        elif button_type == 'elevated':
            base_kwargs.update({
                'fg_color': MaterialColors.get_color('surface_container_low', dark_mode),
                'border_width': 0,
                'text_color': MaterialColors.get_color('primary', dark_mode),
                'hover_color': MaterialColors.get_color('surface_container', dark_mode),
            })

        if size == 'small':
            base_kwargs['height'] = 32
        elif size == 'medium':
            base_kwargs['height'] = 40
        elif size == 'large':
            base_kwargs['height'] = 56

        base_kwargs.update(kwargs)
        super().__init__(master, **base_kwargs)


class MD3Entry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        dark_mode = ctk.get_appearance_mode() == "Dark"
        base_kwargs = {
            'corner_radius': 4,
            'border_width': 2,
            'font': MaterialTypography.BODY_MEDIUM,
            'height': 40,
            'fg_color': MaterialColors.get_color('surface_container_lowest', dark_mode),
            'border_color': MaterialColors.get_color('outline', dark_mode),
            'text_color': MaterialColors.get_color('on_surface', dark_mode),
        }
        base_kwargs.update(kwargs)
        super().__init__(master, **base_kwargs)


class MD3Label(ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        typography = kwargs.pop('typography', 'body_medium')
        font_map = {
            'display_large': MaterialTypography.DISPLAY_LARGE,
            'display_medium': MaterialTypography.DISPLAY_MEDIUM,
            'display_small': MaterialTypography.DISPLAY_SMALL,
            'headline_large': MaterialTypography.HEADLINE_LARGE,
            'headline_medium': MaterialTypography.HEADLINE_MEDIUM,
            'headline_small': MaterialTypography.HEADLINE_SMALL,
            'title_large': MaterialTypography.TITLE_LARGE,
            'title_medium': MaterialTypography.TITLE_MEDIUM,
            'title_small': MaterialTypography.TITLE_SMALL,
            'label_large': MaterialTypography.LABEL_LARGE,
            'label_medium': MaterialTypography.LABEL_MEDIUM,
            'label_small': MaterialTypography.LABEL_SMALL,
            'body_large': MaterialTypography.BODY_LARGE,
            'body_medium': MaterialTypography.BODY_MEDIUM,
            'body_small': MaterialTypography.BODY_SMALL,
        }

        dark_mode = ctk.get_appearance_mode() == "Dark"
        base_kwargs = {
            'font': font_map.get(typography, MaterialTypography.BODY_MEDIUM),
            'text_color': MaterialColors.get_color('on_surface', dark_mode),
        }
        base_kwargs.update(kwargs)
        super().__init__(master, **base_kwargs)


class MD3Card(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        elevation = kwargs.pop('elevation', 1)
        dark_mode = ctk.get_appearance_mode() == "Dark"

        if elevation == 0:
            border_width = 1
            border_color = MaterialColors.get_color('outline_variant', dark_mode)
        else:
            border_width = 0
            border_color = None

        base_kwargs = {
            'corner_radius': 12,
            'border_width': border_width,
            'border_color': border_color,
            'fg_color': MaterialColors.get_color('surface_container', dark_mode),
        }
        base_kwargs.update(kwargs)
        super().__init__(master, **base_kwargs)


class MD3Switch(ctk.CTkSwitch):
    def __init__(self, master, **kwargs):
        dark_mode = ctk.get_appearance_mode() == "Dark"
        base_kwargs = {
            'font': MaterialTypography.LABEL_MEDIUM,
            'fg_color': MaterialColors.get_color('surface_container_high', dark_mode),
            'progress_color': MaterialColors.get_color('primary', dark_mode),
            'button_color': MaterialColors.get_color('on_primary', dark_mode),
            'button_hover_color': MaterialColors.get_color('primary_container', dark_mode),
            'text_color': MaterialColors.get_color('on_surface', dark_mode),
        }
        base_kwargs.update(kwargs)
        super().__init__(master, **base_kwargs)


class MD3SegmentedButton(ctk.CTkSegmentedButton):
    def __init__(self, master, **kwargs):
        dark_mode = ctk.get_appearance_mode() == "Dark"
        base_kwargs = {
            'height': 40,
            'corner_radius': 20,
            'border_width': 1,
            'font': MaterialTypography.LABEL_MEDIUM,
            'fg_color': MaterialColors.get_color('surface_container', dark_mode),
            'selected_color': MaterialColors.get_color('primary', dark_mode),
            'selected_hover_color': MaterialColors.get_color('primary_container', dark_mode),
            'unselected_color': MaterialColors.get_color('surface_container_low', dark_mode),
            'unselected_hover_color': MaterialColors.get_color('surface_container', dark_mode),
            'text_color': MaterialColors.get_color('on_surface', dark_mode),
            'text_color_disabled': MaterialColors.get_color('on_surface_variant', dark_mode),
        }
        base_kwargs.update(kwargs)
        super().__init__(master, **base_kwargs)