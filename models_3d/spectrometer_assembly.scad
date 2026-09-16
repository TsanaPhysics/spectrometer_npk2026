// ==============================================================================
// NPK Spectrometer 2026 - Complete Optical Assembly & Exploded View
// Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
// Department of Physics, Faculty of Science and Technology,
// Rambhai Barni Rajabhat University (RBRU)
//
// Shows:
// 1. Optical Measurement Chamber (Matte Black PLA+)
// 2. Light-Tight Baffle Lid (Exploded / Closed toggle)
// 3. Standard 10mm Optical Glass / Quartz Cuvette (Transparent Cyan)
// 4. Optical Ray / Collimated Light Beam (525nm Green / 625nm Red)
// 5. Adafruit TCS34725 Sensor PCB & WS2812B Grove LED Module
// ==============================================================================

use <cuvette_optical_chamber.scad>
use <light_tight_lid.scad>

// --- Assembly View Controls ---
exploded_distance = 35.0; // Set to 0 for closed, 35 for exploded view
show_optical_ray  = true; // Show light beam passing through cuvette
show_cutaway      = false;// Set true to see inside cross-section

// Colors
color_chamber = [0.18, 0.18, 0.18, 1.0]; // Matte Black
color_lid     = [0.22, 0.22, 0.22, 1.0]; // Matte Dark Grey
color_cuvette = [0.40, 0.85, 0.95, 0.45]; // Transparent Optical Glass
color_beam    = [0.10, 0.90, 0.20, 0.85]; // 525nm Green Beam
color_pcb_led = [0.85, 0.20, 0.20, 0.90]; // Red PCB (Grove)
color_pcb_tcs = [0.15, 0.35, 0.85, 0.90]; // Blue PCB (Adafruit)

module full_spectrometer_assembly() {
    difference() {
        union() {
            // 1. Optical Measurement Chamber
            color(color_chamber)
                optical_chamber();

            // 2. Standard 10mm Cuvette (12.5 x 12.5 x 45 mm)
            // Sitting on 3.0mm floor
            color(color_cuvette) {
                translate([-12.5/2, -12.5/2, 3.0]) {
                    difference() {
                        cube([12.5, 12.5, 45.0]);
                        // Liquid sample core
                        translate([1.25, 1.25, 1.25])
                            cube([10.0, 10.0, 44.0]);
                    }
                }
            }

            // 3. Collimated Optical Ray (3mm diameter through optical axis Z=18mm)
            if (show_optical_ray) {
                color(color_beam) {
                    translate([-28, 0, 18.0])
                        rotate([0, 90, 0])
                            cylinder(d=3.0, h=56, $fn=30);
                }
            }

            // 4. WS2812B NeoPixel Module (Left Side, -X)
            color(color_pcb_led) {
                translate([-23.0 - 1.6, -10.0, 18.0 - 10.0])
                    cube([1.6, 20.0, 20.0]);
            }

            // 5. Adafruit TCS34725 Sensor Module (Right Side, +X)
            color(color_pcb_tcs) {
                translate([23.0, -10.0, 18.0 - 10.0])
                    cube([1.6, 20.0, 20.0]);
            }

            // 6. Light-Tight Baffle Lid (with exploded height)
            color(color_lid) {
                translate([0, 0, 36.0 + exploded_distance])
                    light_tight_lid();
            }
        }

        // Cutaway view for internal inspection
        if (show_cutaway) {
            translate([0, -50, -10])
                cube([100, 100, 120]);
        }
    }
}

full_spectrometer_assembly();
