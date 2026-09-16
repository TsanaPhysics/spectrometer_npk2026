// ==============================================================================
// Kingdom of Thailand - 3D Topographic Model
// Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
// Department of Physics, Faculty of Science and Technology,
// Rambhai Barni Rajabhat University (RBRU)
// ==============================================================================

// --- User Parameters ---
model_scale_x       = 1.0;   // Scaling factor X
model_scale_y       = 1.0;   // Scaling factor Y
relief_multiplier   = 1.0;   // Vertical terrain exaggeration (1.0x - 3.0x)
base_pedestal_h     = 2.0;   // Additional base thickness (mm)

// Mode Selection: "plinth" or "standalone"
mode = "plinth"; 

module thailand_display_plinth() {
    scale([model_scale_x, model_scale_y, relief_multiplier])
        import("thailand_topographic_map_3d.stl");
}

module thailand_standalone_country() {
    scale([model_scale_x, model_scale_y, relief_multiplier])
        import("thailand_country_standalone_3d.stl");
}

if (mode == "plinth") {
    thailand_display_plinth();
} else if (mode == "standalone") {
    thailand_standalone_country();
}
