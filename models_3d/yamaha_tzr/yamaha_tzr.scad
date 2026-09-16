// ==============================================================================
// Yamaha TZR Series - Parametric 3D CAD Architecture
// Designed with Skill: motorcycle-3d-cad-architect
// Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
// Department of Physics, Faculty of Science and Technology,
// Rambhai Barni Rajabhat University (RBRU)
//
// Key Features:
// 1. Yamaha Deltabox Aluminum Twin-Spar Frame
// 2. 2-Stroke Liquid-Cooled Engine with YPVS (Yamaha Power Valve System)
// 3. Tuned Racing Expansion Chamber Exhaust (Diffuser, Belly, Baffle & Silencer)
// 4. Aerodynamic 90s Racing Fairing with NACA Ducts & Bubble Windscreen
// 5. 17-inch 3-Spoke Sport Alloy Wheels with Disc Rotors
// 6. Monocross / Monoshock Rear Suspension & Box-Section Swingarm
// ==============================================================================

$fn = 36; // Curve smoothness

// --- User Parameters ---
scale_factor        = 1.0;   // Scale factor (1.0 = 1:10 scale, L ~ 200mm)
show_fairing        = true;  // Toggle outer racing fairings
show_paddock_stand  = true;  // Toggle racing paddock display stand
show_cutaway        = false; // Cross-section cutaway mode

// Color Palette (Classic Yamaha Racing Livery)
color_fairing_white = [0.95, 0.95, 0.95, 1.0];
color_fairing_red   = [0.85, 0.12, 0.12, 1.0];
color_windscreen    = [0.20, 0.60, 0.90, 0.45];
color_deltabox      = [0.78, 0.80, 0.82, 1.0]; // Polished Aluminum
color_engine        = [0.28, 0.28, 0.30, 1.0]; // Dark Graphite Case
color_exhaust       = [0.18, 0.18, 0.20, 1.0]; // Heat-treated Steel
color_silencer      = [0.85, 0.85, 0.88, 1.0]; // Brushed Aluminum
color_tire          = [0.12, 0.12, 0.14, 1.0]; // Rubber
color_rim           = [0.95, 0.95, 0.95, 1.0]; // White Racing Wheels
color_seat          = [0.15, 0.15, 0.15, 1.0]; // Black Vinyl
color_stand         = [0.85, 0.15, 0.15, 1.0]; // Red Paddock Stand

// Dimensions (1:10 Scale in mm)
wheelbase           = 135.0; // Front axle at +67.5, Rear axle at -67.5
wheel_radius        = 30.0;  // 17" Wheel equivalent

// --- Module: Wheels & Brakes ---
module tzr_wheel(x_pos, is_rear=false) {
    width_tire = is_rear ? 15.0 : 11.0;
    r_tire     = is_rear ? 6.5 : 5.5;
    r_major    = 30.0 - r_tire;
    
    translate([x_pos, 0, 30.0]) {
        // Rubber Tire (Torus)
        color(color_tire)
            rotate([90, 0, 0])
                rotate_extrude()
                    translate([r_major, 0, 0])
                        circle(r=r_tire);
                        
        // Alloy Rim (Ring)
        color(color_rim) {
            rotate([90, 0, 0])
                difference() {
                    cylinder(r=21.0, h=width_tire - 2, center=true);
                    cylinder(r=18.0, h=width_tire, center=true);
                }
            // Center Hub
            rotate([90, 0, 0])
                cylinder(r=6.5, h=width_tire + 2, center=true);
                
            // 3-Spoke Sport Design
            for (ang = [0, 120, 240]) {
                rotate([0, ang, 0])
                    translate([0, 0, 10.0])
                        cube([4.0, 3.5, 18.0], center=true);
            }
        }
        
        // Brake Rotors
        color([0.7, 0.7, 0.75, 1.0]) {
            if (!is_rear) {
                // Front Twin Discs
                for (s = [-1, 1]) {
                    translate([0, s * 6.5, 0])
                        rotate([90, 0, 0])
                            cylinder(r=15.5, h=1.2, center=true);
                    // Caliper
                    translate([-10.0, s * 7.5, 3.0])
                        cube([8.0, 3.5, 10.0], center=true);
                }
            } else {
                // Rear Single Disc (Right side)
                translate([0, -6.5, 0])
                    rotate([90, 0, 0])
                        cylinder(r=13.0, h=1.2, center=true);
                // Chain Sprocket (Left side)
                translate([0, 7.0, 0])
                    rotate([90, 0, 0])
                        cylinder(r=14.5, h=1.5, center=true);
            }
        }
    }
}

// --- Module: Front Fork & Triple Clamps ---
module tzr_front_fork() {
    translate([0, 0, 0]) {
        // Telescopic Fork Legs
        color(color_deltabox) {
            for (s = [-1, 1]) {
                // Stanchion (Chrome Upper)
                hull() {
                    translate([38.0, s * 11.5, 74.0]) sphere(r=3.2);
                    translate([52.0, s * 11.5, 52.0]) sphere(r=3.2);
                }
                // Slider (Lower Cast)
                hull() {
                    translate([52.0, s * 11.5, 52.0]) sphere(r=4.5);
                    translate([67.5, s * 11.5, 30.0]) sphere(r=4.5);
                }
            }
            // Triple Clamps
            translate([38.0, 0, 74.0]) cube([8.0, 27.0, 4.0], center=true);
            translate([42.0, 0, 65.0]) cube([9.0, 27.0, 5.0], center=true);
        }
        
        // Clip-on Handlebars
        color([0.2, 0.2, 0.22, 1.0]) {
            for (s = [-1, 1]) {
                hull() {
                    translate([38.0, s * 11.5, 74.0]) sphere(r=2.5);
                    translate([30.0, s * 31.0, 69.0]) sphere(r=2.5);
                }
                // Grips
                hull() {
                    translate([33.0, s * 23.0, 70.5]) sphere(r=3.2);
                    translate([30.0, s * 31.0, 69.0]) sphere(r=3.2);
                }
            }
        }
        
        // Cockpit Instrument Cluster
        color([0.15, 0.15, 0.15, 1.0]) {
            translate([43.0,  6.0, 77.0]) cylinder(r=5.5, h=4.0, center=true);
            translate([43.0, -6.0, 77.0]) cylinder(r=5.5, h=4.0, center=true);
        }
    }
}

// --- Module: Deltabox Aluminum Frame ---
module tzr_deltabox_frame() {
    color(color_deltabox) {
        // Steering Head
        translate([38.0, 0, 70.0])
            cylinder(r=7.0, h=16.0, center=true);
            
        // Left & Right Twin-Spar Beams
        for (s = [-1, 1]) {
            // Forward Beam
            hull() {
                translate([36.0, s * 11.0, 70.0]) sphere(r=6.5);
                translate([15.0, s * 16.0, 60.0]) sphere(r=7.5);
            }
            // Rear Diagonal Beam to Swingarm Pivot
            hull() {
                translate([15.0, s * 16.0, 60.0]) sphere(r=7.5);
                translate([-25.0, s * 18.0, 38.0]) sphere(r=8.5);
            }
            // Down-tubes / Engine Cradle
            hull() {
                translate([34.0, s * 9.0, 64.0]) sphere(r=3.2);
                translate([-2.0, s * 12.0, 26.0]) sphere(r=3.2);
            }
            hull() {
                translate([-2.0, s * 12.0, 26.0]) sphere(r=3.2);
                translate([-22.0, s * 14.0, 27.0]) sphere(r=3.5);
            }
            // Rear Subframe Tubes
            hull() {
                translate([-25.0, s * 16.0, 44.0]) sphere(r=3.0);
                translate([-78.0, s * 9.0, 66.0]) sphere(r=3.0);
            }
            hull() {
                translate([-25.0, s * 16.0, 38.0]) sphere(r=2.8);
                translate([-55.0, s * 11.0, 58.0]) sphere(r=2.8);
            }
            // Footpegs
            translate([-24.0, s * 22.0, 33.0])
                rotate([90, 0, 0]) cylinder(r=2.5, h=10.0, center=true);
        }
        
        // Frame Cross-Brace
        translate([12.0, 0, 63.0])
            cube([10.0, 26.0, 7.0], center=true);
    }
}

// --- Module: 2-Stroke YPVS Engine & Radiator ---
module tzr_engine() {
    // Crankcase
    color(color_engine) {
        translate([-7.0, 0, 33.0])
            cube([28.0, 24.0, 20.0], center=true);
            
        // Right Clutch Casing
        translate([-7.0, -13.0, 33.0])
            rotate([90, 0, 0])
                cylinder(r=10.5, h=5.0, center=true);
                
        // Left Magneto Cover
        translate([-7.0, 13.0, 33.0])
            rotate([90, 0, 0])
                cylinder(r=9.5, h=4.5, center=true);
                
        // Slanted Cylinder Block (45 degrees forward)
        hull() {
            translate([-2.0, 0, 40.0]) sphere(r=9.5);
            translate([13.0, 0, 55.0]) sphere(r=9.0);
        }
        // Cylinder Head & Fins
        translate([15.0, 0, 57.0])
            sphere(r=8.5);
            
        // YPVS Chamber (Yamaha Power Valve System)
        translate([13.0, 0, 51.0])
            rotate([90, 0, 0])
                cylinder(r=4.2, h=18.0, center=true);
    }
    
    // Curved Radiator (Behind front wheel)
    color([0.35, 0.38, 0.40, 1.0]) {
        translate([27.0, 0, 45.0])
            cube([5.0, 32.0, 18.0], center=true);
    }
}

// --- Module: Tuned Expansion Chamber Exhaust ---
module tzr_expansion_chamber() {
    color(color_exhaust) {
        // Header Pipe exiting front of cylinder
        hull() {
            translate([14.0, 0, 49.0]) sphere(r=3.8);
            translate([14.0, -5.0, 32.0]) sphere(r=4.2);
        }
        hull() {
            translate([14.0, -5.0, 32.0]) sphere(r=4.2);
            translate([8.0, -9.0, 22.0]) sphere(r=5.0);
        }
        // Divergent Cone (Expansion)
        hull() {
            translate([8.0, -9.0, 22.0]) sphere(r=5.0);
            translate([-6.0, -15.0, 20.0]) sphere(r=8.5);
        }
        // Belly Resonant Section
        hull() {
            translate([-6.0, -15.0, 20.0]) sphere(r=8.5);
            translate([-24.0, -16.0, 21.0]) sphere(r=8.8);
        }
        // Convergent Baffle Cone (Wave reflection taper)
        hull() {
            translate([-24.0, -16.0, 21.0]) sphere(r=8.8);
            translate([-46.0, -18.0, 29.0]) sphere(r=3.8);
        }
        // Stinger Pipe
        hull() {
            translate([-46.0, -18.0, 29.0]) sphere(r=3.8);
            translate([-52.0, -19.0, 34.0]) sphere(r=3.2);
        }
    }
    
    // Upswept Aluminum Racing Silencer
    color(color_silencer) {
        hull() {
            translate([-52.0, -19.0, 34.0]) sphere(r=5.8);
            translate([-85.0, -23.0, 48.0]) sphere(r=5.8);
        }
        // Exhaust Tip
        translate([-86.5, -23.2, 48.8])
            rotate([0, -22, -6])
                cylinder(r=2.5, h=3.5, center=true);
    }
}

// --- Module: Swingarm & Monoshock ---
module tzr_swingarm() {
    color(color_deltabox) {
        // Left and Right Arms
        for (s = [-1, 1]) {
            hull() {
                translate([-25.0, s * 17.0, 38.0]) sphere(r=4.0);
                translate([-67.5, s * 11.5, 30.0]) sphere(r=4.0);
            }
        }
        // Pivot cross tube
        translate([-25.0, 0, 38.0])
            rotate([90, 0, 0]) cylinder(r=5.5, h=34.0, center=true);
        // Stabilizer Arch
        translate([-42.0, 0, 38.0])
            rotate([90, 0, 0]) cylinder(r=3.8, h=28.0, center=true);
    }
    
    // Monoshock Damper
    color([0.85, 0.85, 0.20, 1.0]) {
        hull() {
            translate([-22.0, 0, 52.0]) sphere(r=4.5);
            translate([-32.0, 0, 36.0]) sphere(r=4.5);
        }
    }
}

// --- Module: Bodywork, Fairing, Tank, Seat & Tail ---
module tzr_bodywork() {
    // Fuel Tank
    color(color_fairing_red) {
        difference() {
            translate([7.0, 0, 64.0])
                scale([2.4, 1.7, 1.1]) sphere(r=10.0);
            // Knee Indents
            translate([-2.0,  19.0, 63.0]) sphere(r=10.0);
            translate([-2.0, -19.0, 63.0]) sphere(r=10.0);
        }
        // Aircraft Filler Cap
        color([0.7, 0.7, 0.75, 1.0])
            translate([9.0, 0, 75.0]) cylinder(r=4.2, h=2.5, center=true);
    }
    
    // Racing Stepped Seat
    color(color_seat) {
        // Rider Seat
        translate([-28.0, 0, 60.5]) cube([24.0, 24.0, 6.0], center=true);
        // Pillion Step
        translate([-46.0, 0, 65.5]) cube([16.0, 20.0, 7.0], center=true);
    }
    
    // Tail Cowl
    color(color_fairing_white) {
        hull() {
            translate([-45.0, 0, 65.0]) cube([8.0, 26.0, 12.0], center=true);
            translate([-90.0, 0, 71.0]) cube([4.0, 12.0, 8.0], center=true);
        }
        // Taillight
        color([0.9, 0.1, 0.1, 1.0])
            translate([-91.0, 0, 71.0]) cube([3.0, 10.0, 6.0], center=true);
    }
    
    // Aerodynamic Upper Fairing & Nose Cone
    if (show_fairing) {
        color(color_fairing_white) {
            difference() {
                translate([55.0, 0, 69.0])
                    scale([2.5, 1.8, 1.3]) sphere(r=10.0);
                // Cutout inner cockpit
                translate([48.0, 0, 65.0]) cube([32.0, 28.0, 20.0], center=true);
            }
            // Side Lower Fairings with NACA cooling ducts
            for (s = [-1, 1]) {
                difference() {
                    translate([24.0, s * 19.0, 50.0])
                        cube([40.0, 4.0, 24.0], center=true);
                    // NACA Duct cutout
                    translate([20.0, s * 19.0, 48.0])
                        rotate([0, 45, 0]) cube([12.0, 6.0, 12.0], center=true);
                }
            }
            // Front Hugger Mudguard
            translate([67.5, 0, 30.0])
                rotate([90, 0, 0])
                    difference() {
                        cylinder(r=28.0, h=16.0, center=true);
                        cylinder(r=25.0, h=18.0, center=true);
                        // Clip lower half
                        translate([0, -25.0, 0]) cube([60.0, 50.0, 20.0], center=true);
                    }
        }
        
        // Headlight
        color([1.0, 0.95, 0.7, 1.0])
            translate([77.0, 0, 67.5]) cube([4.0, 19.0, 9.0], center=true);
            
        // Bubble Windscreen
        color(color_windscreen) {
            hull() {
                translate([55.0, 0, 75.0]) cube([6.0, 22.0, 2.0], center=true);
                translate([32.0, 0, 93.0]) cube([4.0, 10.0, 2.0], center=true);
            }
        }
    }
}

// --- Module: Racing Paddock Stand & Display Base ---
module tzr_paddock_stand() {
    if (show_paddock_stand) {
        color(color_stand) {
            for (s = [-1, 1]) {
                hull() {
                    translate([-67.5, s * 24.0, 30.0]) sphere(r=2.5);
                    translate([-85.0, s * 24.0, 3.0])  sphere(r=2.5);
                }
                hull() {
                    translate([-85.0, s * 24.0, 3.0])  sphere(r=2.5);
                    translate([-100.0, s * 24.0, 3.0]) sphere(r=2.5);
                }
                hull() {
                    translate([-67.5, s * 13.0, 30.0]) sphere(r=2.2);
                    translate([-67.5, s * 24.0, 30.0]) sphere(r=2.2);
                }
            }
            // Rear Crossbar handle
            hull() {
                translate([-100.0, -24.0, 3.0]) sphere(r=2.5);
                translate([-100.0,  24.0, 3.0]) sphere(r=2.5);
            }
        }
        
        // Solid Display Base Plinth
        color([0.15, 0.15, 0.18, 1.0]) {
            translate([-5.0, 0, 1.25])
                cube([210.0, 68.0, 2.5], center=true);
        }
    }
}

// --- Master Assembly ---
module yamaha_tzr_complete() {
    scale([scale_factor, scale_factor, scale_factor]) {
        tzr_wheel(67.5, is_rear=false);
        tzr_wheel(-67.5, is_rear=true);
        tzr_front_fork();
        tzr_deltabox_frame();
        tzr_engine();
        tzr_expansion_chamber();
        tzr_swingarm();
        tzr_bodywork();
        tzr_paddock_stand();
    }
}

// Render Master Assembly
yamaha_tzr_complete();
