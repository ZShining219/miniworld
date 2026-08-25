use serde::{Deserialize, Serialize};
use std::{fs, path::PathBuf};
use tauri::{LogicalPosition, LogicalSize, Manager, WindowEvent};

const MIN_WIDTH: f64 = 320.0;
const MIN_HEIGHT: f64 = 320.0;
const MAX_WIDTH: f64 = 900.0;
const MAX_HEIGHT: f64 = 700.0;

#[derive(Debug, Deserialize, Serialize)]
struct WindowGeometry {
    x: f64,
    y: f64,
    width: f64,
    height: f64,
}

fn geometry_path(app: &tauri::AppHandle) -> Option<PathBuf> {
    app.path()
        .app_config_dir()
        .ok()
        .map(|directory| directory.join("radar-window.json"))
}

fn load_geometry(app: &tauri::AppHandle) -> Option<WindowGeometry> {
    let path = geometry_path(app)?;
    let content = fs::read_to_string(path).ok()?;
    serde_json::from_str(&content).ok()
}

fn save_geometry(app: &tauri::AppHandle, geometry: &WindowGeometry) {
    let Some(path) = geometry_path(app) else {
        return;
    };
    let Some(parent) = path.parent() else {
        return;
    };
    if fs::create_dir_all(parent).is_err() {
        return;
    }
    let Ok(content) = serde_json::to_vec(geometry) else {
        return;
    };
    let _ = fs::write(path, content);
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            let Some(window) = app.get_webview_window("main") else {
                return Ok(());
            };
            if let Some(geometry) = load_geometry(app.handle()) {
                let width = geometry.width.clamp(MIN_WIDTH, MAX_WIDTH);
                let height = geometry.height.clamp(MIN_HEIGHT, MAX_HEIGHT);
                let _ = window.set_size(LogicalSize::new(width, height));
                let _ = window.set_position(LogicalPosition::new(geometry.x, geometry.y));
            }
            #[cfg(debug_assertions)]
            if std::env::var_os("MINIWORLD_RADAR_QA_EXPANDED").is_some() {
                let _ = window.set_size(LogicalSize::new(MAX_WIDTH, MAX_HEIGHT));
                let _ = window.set_position(LogicalPosition::new(120.0, 120.0));
            }
            Ok(())
        })
        .on_window_event(|window, event| {
            if !matches!(event, WindowEvent::Moved(_) | WindowEvent::Resized(_)) {
                return;
            }
            let Ok(scale_factor) = window.scale_factor() else {
                return;
            };
            let (Ok(position), Ok(size)) = (window.outer_position(), window.inner_size()) else {
                return;
            };
            let position = position.to_logical::<f64>(scale_factor);
            let size = size.to_logical::<f64>(scale_factor);
            save_geometry(
                window.app_handle(),
                &WindowGeometry {
                    x: position.x,
                    y: position.y,
                    width: size.width.clamp(MIN_WIDTH, MAX_WIDTH),
                    height: size.height.clamp(MIN_HEIGHT, MAX_HEIGHT),
                },
            );
        })
        .run(tauri::generate_context!())
        .expect("failed to run the MiniWorld radar window");
}
