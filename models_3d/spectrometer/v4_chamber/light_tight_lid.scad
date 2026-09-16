// ==============================================================================
// NPK Spectrometer 2026 - Light-Tight Labyrinth Baffle Lid
// Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
// Department of Physics, Faculty of Science and Technology,
// Rambhai Barni Rajabhat University (RBRU)
//
// Features:
// 1. Dual-stepped labyrinth seal (Baffle Joint) completely blocks ambient light
// 2. Internal headroom accommodates cuvette top without physical pressure
// 3. Ergonomic ribbed grip handle for one-handed operation during field assays
// 4. Chamfered leading edges for smooth mating with chamber rim
// ==============================================================================

$fn = 60; // Curve resolution

// --- Global Parametric Dimensions ---
tolerance              = 0.25;  // 3D printing clearance (mm)

// Chamber mating dimensions
body_w                 = 46.00; 
body_d                 = 30.00;
baffle_step_w          = 2.20;  // Shoulder step width on chamber
baffle_h               = 3.50;  // Height of chamber baffle lip

// Lid dimensions
lid_w                  = body_w + 2.0; // 48.0 mm
lid_d                  = body_d + 2.0; // 32.0 mm
lid_skirt_overlap      = 5.00;         // Depth skirt goes down around chamber
lid_roof_th            = 3.50;         // Thickness of lid top roof
lid_total_h            = lid_skirt_overlap + baffle_h + 12.00 + lid_roof_th; // 24.0 mm

// Internal Cuvette Clearance Cavity
cuvette_pocket_w       = 14.00;        // Clearance for 12.5mm cuvette
cuvette_pocket_d       = 14.00;
cuvette_pocket_h       = baffle_h + 12.00; // 15.5 mm headroom

// Handle Dimensions
handle_w               = 18.00;
handle_d               = 8.00;
handle_h               = 12.00;

// ==============================================================================
// Main Lid Module
// ==============================================================================
module light_tight_lid() {
    difference() {
        // --- 1. POSITIVE SOLID BODY ---
        union() {
            // Main Outer Lid Shell (Rounded Box)
            hull() {
                translate([-lid_w/2 + 2.5, -lid_d/2 + 2.5, 0]) cylinder(r=2.5, h=lid_total_h);
                translate([ lid_w/2 - 2.5, -lid_d/2 + 2.5, 0]) cylinder(r=2.5, h=lid_total_h);
                translate([ lid_w/2 - 2.5,  lid_d/2 - 2.5, 0]) cylinder(r=2.5, h=lid_total_h);
                translate([-lid_w/2 + 2.5,  lid_d/2 - 2.5, 0]) cylinder(r=2.5, h=lid_total_h);
            }

            // Top Ergonomic Grip Handle with Textured Ribs
            translate([0, 0, lid_total_h]) {
                hull() {
                    translate([-handle_w/2 + 2, -handle_d/2 + 2, 0]) cylinder(r=2, h=handle_h);
                    translate([ handle_w/2 - 2, -handle_d/2 + 2, 0]) cylinder(r=2, h=handle_h);
                    translate([ handle_w/2 - 2,  handle_d/2 - 2, 0]) cylinder(r=2, h=handle_h);
                    translate([-handle_w/2 + 2,  handle_d/2 - 2, 0]) cylinder(r=2, h=handle_h);
                }
                
                // Grip texture ribs
                for (i = [-handle_w/2 + 3 : 2.5 : handle_w/2 - 3]) {
                    translate([i, 0, handle_h/2])
                        cube([1.0, handle_d + 1.2, handle_h - 2], center=true);
                }
            }
        }

        // --- 2. NEGATIVE LABYRINTH CAVITIES ---
        
        // 2.1 Outer Skirt Recess (Fits over chamber body outer perimeter)
        translate([0, 0, -0.1]) {
            hull() {
                translate([-(body_w/2 + tolerance) + 2, -(body_d/2 + tolerance) + 2, 0])
                    cylinder(r=2, h=lid_skirt_overlap + 0.1);
                translate([ (body_w/2 + tolerance) - 2, -(body_d/2 + tolerance) + 2, 0])
                    cylinder(r=2, h=lid_skirt_overlap + 0.1);
                translate([ (body_w/2 + tolerance) - 2,  (body_d/2 + tolerance) - 2, 0])
                    cylinder(r=2, h=lid_skirt_overlap + 0.1);
                translate([-(body_w/2 + tolerance) + 2,  (body_d/2 + tolerance) - 2, 0])
                    cylinder(r=2, h=lid_skirt_overlap + 0.1);
            }
        }

        // 2.2 Stepped Inner Labyrinth Groove (Fits over raised baffle lip)
        inner_lip_w = body_w - (2 * baffle_step_w) + (2 * tolerance);
        inner_lip_d = body_d - (2 * baffle_step_w) + (2 * tolerance);
        
        translate([0, 0, lid_skirt_overlap - 0.1]) {
            hull() {
                translate([-inner_lip_w/2 + 1.5, -inner_lip_d/2 + 1.5, 0])
                    cylinder(r=1.5, h=baffle_h + 1.0);
                translate([ inner_lip_w/2 - 1.5, -inner_lip_d/2 + 1.5, 0])
                    cylinder(r=1.5, h=baffle_h + 1.0);
                translate([ inner_lip_w/2 - 1.5,  inner_lip_d/2 - 1.5, 0])
                    cylinder(r=1.5, h=baffle_h + 1.0);
                translate([-inner_lip_w/2 + 1.5,  inner_lip_d/2 - 1.5, 0])
                    cylinder(r=1.5, h=baffle_h + 1.0);
            }
        }

        // 2.3 Center Cuvette Headroom Pocket
        translate([-cuvette_pocket_w/2, -cuvette_pocket_d/2, lid_skirt_overlap + baffle_h])
            cube([cuvette_pocket_w, cuvette_pocket_d, cuvette_pocket_h]);

        // Entry chamfer for smooth sliding
        translate([0, 0, -0.1])
            cylinder(r1=body_w/2 + 1, r2=body_w/2 - 2, h=1.5);
    }
}

// Render the lid (oriented in printing position with skirt opening down)
light_tight_lid();
