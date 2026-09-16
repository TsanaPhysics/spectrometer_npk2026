// ==============================================================================
// NPK Spectrometer 2026 - Optical Measurement Chamber (Cuvette Holder)
// Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
// Department of Physics, Faculty of Science and Technology,
// Rambhai Barni Rajabhat University (RBRU)
//
// Features:
// 1. Standard 10 mm cuvette slot (12.5 x 12.5 mm + 0.25 mm tolerance)
// 2. Coaxial optical axis at Z = 15.0 mm above cuvette seat floor
// 3. Dual 3.0 mm collimating apertures (Input from WS2812B, Output to TCS34725)
// 4. Adafruit TCS34725 & Grove RGB LED mounting pockets with M2.5 screw posts
// 5. Labyrinth light-tight baffle ridge on top rim
// 6. 4x M3 base mounting flange for lab bench stability
// ==============================================================================

$fn = 60; // Curve resolution

// --- Global Parametric Dimensions ---
tolerance              = 0.25;  // 3D printing clearance (mm)
cuvette_w              = 12.50 + tolerance; // 12.75 mm
cuvette_d              = 12.50 + tolerance; // 12.75 mm
cuvette_floor_th       = 3.00;  // Floor under cuvette
cuvette_well_depth     = 30.00; // Well depth (cuvette extends 15mm above for easy grab)

optical_axis_z         = cuvette_floor_th + 15.00; // 18.00 mm from chamber bottom
aperture_dia           = 3.00;  // Collimating aperture diameter
aperture_len           = 3.50;  // Collimating aperture tunnel length

// Chamber body dimensions
body_w                 = 46.00; // X dimension (along optical axis)
body_d                 = 30.00; // Y dimension
body_h                 = 36.00; // Z height of main block

// Top Labyrinth Baffle Rim
baffle_h               = 3.50;  // Height of raised light-tight rim
baffle_step_w          = 2.20;  // Width of outer shoulder step

// Sensor & LED Mountings
led_pocket_w           = 21.00; // Grove LED PCB width
led_pocket_h           = 21.00; // Grove LED PCB height
led_pocket_depth       = 3.20;  // Recess depth for LED PCB
sensor_pocket_w        = 21.00; // Adafruit TCS34725 width
sensor_pocket_h        = 21.00; // Adafruit TCS34725 height
sensor_pocket_depth    = 3.20;  // Recess depth for TCS34725
sensor_screw_pitch     = 15.00; // M2.5 mounting hole pitch
screw_m25_dia          = 2.20;  // Pilot hole for M2.5 self-tapping screws

// Base Flange Dimensions
flange_w               = 64.00;
flange_d               = 48.00;
flange_h               = 3.00;
flange_hole_pitch_x    = 54.00;
flange_hole_pitch_y    = 38.00;
flange_m3_dia          = 3.40;  // M3 bolt clearance hole

// ==============================================================================
// Main Module
// ==============================================================================
module optical_chamber() {
    difference() {
        // --- 1. POSITIVE SOLID BODY ---
        union() {
            // Main optical housing block (rounded corners)
            hull() {
                translate([-body_w/2 + 2, -body_d/2 + 2, 0]) cylinder(r=2, h=body_h);
                translate([ body_w/2 - 2, -body_d/2 + 2, 0]) cylinder(r=2, h=body_h);
                translate([ body_w/2 - 2,  body_d/2 - 2, 0]) cylinder(r=2, h=body_h);
                translate([-body_w/2 + 2,  body_d/2 - 2, 0]) cylinder(r=2, h=body_h);
            }
            
            // Raised Labyrinth Baffle Lip on top
            translate([0, 0, body_h]) {
                hull() {
                    translate([-(body_w/2 - baffle_step_w) + 1.5, -(body_d/2 - baffle_step_w) + 1.5, 0]) cylinder(r=1.5, h=baffle_h);
                    translate([ (body_w/2 - baffle_step_w) - 1.5, -(body_d/2 - baffle_step_w) + 1.5, 0]) cylinder(r=1.5, h=baffle_h);
                    translate([ (body_w/2 - baffle_step_w) - 1.5,  (body_d/2 - baffle_step_w) - 1.5, 0]) cylinder(r=1.5, h=baffle_h);
                    translate([-(body_w/2 - baffle_step_w) + 1.5,  (body_d/2 - baffle_step_w) - 1.5, 0]) cylinder(r=1.5, h=baffle_h);
                }
            }

            // Base mounting flange
            hull() {
                translate([-flange_w/2 + 4, -flange_d/2 + 4, 0]) cylinder(r=4, h=flange_h);
                translate([ flange_w/2 - 4, -flange_d/2 + 4, 0]) cylinder(r=4, h=flange_h);
                translate([ flange_w/2 - 4,  flange_d/2 - 4, 0]) cylinder(r=4, h=flange_h);
                translate([-flange_w/2 + 4,  flange_d/2 - 4, 0]) cylinder(r=4, h=flange_h);
            }
        }

        // --- 2. NEGATIVE CAVITIES & CUTOUTS ---
        
        // 2.1 Cuvette Vertical Well
        translate([-cuvette_w/2, -cuvette_d/2, cuvette_floor_th])
            cube([cuvette_w, cuvette_d, body_h + baffle_h + 1]);

        // Cuvette insertion chamfer / lead-in at top
        translate([0, 0, body_h + baffle_h - 1.5])
            cylinder(r1=cuvette_w/2, r2=cuvette_w/2 + 1.5, h=2.5);

        // 2.2 Coaxial Optical Apertures (Along X-Axis)
        // Light path goes straight through from X = -20 to X = +20
        translate([-body_w/2 - 1, 0, optical_axis_z])
            rotate([0, 90, 0])
                cylinder(d=aperture_dia, h=body_w + 2);

        // 2.3 LED Side Pocket (Left: -X direction)
        translate([-body_w/2 - 0.1, -led_pocket_w/2, optical_axis_z - led_pocket_h/2])
            cube([led_pocket_depth, led_pocket_w, led_pocket_h]);

        // Cable pass-through / screw holes for LED side
        translate([-body_w/2 + led_pocket_depth - 0.1, -sensor_screw_pitch/2, optical_axis_z])
            rotate([0, 90, 0]) cylinder(d=screw_m25_dia, h=6);
        translate([-body_w/2 + led_pocket_depth - 0.1,  sensor_screw_pitch/2, optical_axis_z])
            rotate([0, 90, 0]) cylinder(d=screw_m25_dia, h=6);

        // 2.4 Sensor Side Pocket (Right: +X direction)
        translate([body_w/2 - sensor_pocket_depth + 0.1, -sensor_pocket_w/2, optical_axis_z - sensor_pocket_h/2])
            cube([sensor_pocket_depth + 1, sensor_pocket_w, sensor_pocket_h]);

        // TCS34725 M2.5 mounting screw pilot holes
        translate([body_w/2 - sensor_pocket_depth - 5, -sensor_screw_pitch/2, optical_axis_z])
            rotate([0, 90, 0]) cylinder(d=screw_m25_dia, h=6);
        translate([body_w/2 - sensor_pocket_depth - 5,  sensor_screw_pitch/2, optical_axis_z])
            rotate([0, 90, 0]) cylinder(d=screw_m25_dia, h=6);

        // 2.5 Base Flange M3 Mounting Holes (4x corners)
        translate([-flange_hole_pitch_x/2, -flange_hole_pitch_y/2, -1]) cylinder(d=flange_m3_dia, h=flange_h + 2);
        translate([ flange_hole_pitch_x/2, -flange_hole_pitch_y/2, -1]) cylinder(d=flange_m3_dia, h=flange_h + 2);
        translate([ flange_hole_pitch_x/2,  flange_hole_pitch_y/2, -1]) cylinder(d=flange_m3_dia, h=flange_h + 2);
        translate([-flange_hole_pitch_x/2,  flange_hole_pitch_y/2, -1]) cylinder(d=flange_m3_dia, h=flange_h + 2);
        
        // Cable relief channels at bottom (for neat routing of Grove cables)
        translate([0, -body_d/2 - 1, 0])
            cube([10, 4, 2.5], center=true);
    }
}

// Render the chamber
optical_chamber();
