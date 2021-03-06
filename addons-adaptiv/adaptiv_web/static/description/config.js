const fs = require('fs');
const path = require('path');
const util = require('util');
const merge = require('lodash/merge');
const reduce = require('lodash/reduce');
const sharp = require('sharp');
const devices = require('puppeteer/DeviceDescriptors');
const Promise = require('bluebird');
const querystring = require('querystring');
const urlJoin = require('url-join');

const readFileAsync = util.promisify(fs.readFile);
const writeFileAsync = util.promisify(fs.writeFile);
const timeout = ms => new Promise(res => setTimeout(res, ms));


const SCENE_DEFAULTS = {
  objects: {
    light: {
      material: {
        0: {
          type: 'ShaderNodeEmission',
          inputs: {
            0: '(1,1,1,1)', // Color
            1: 1 // Strength
          }
        }
      }
    },
    floor: {
      material: {
        0: {
          type: 'ShaderNodeBsdfPrincipled',
          inputs: {
            0: '(0.85, 0.85, 0.85, 1)', // Color
            7: 1 // Roughness
          }
        }
      }
    }
  }
}

const THEMES = {
  adaptiv: {

  },
  odoo: {

  },
  industrial: {

  },
  candy: {

  },
  emerald: {

  },
  brave: {

  }
};

const DEFAULT_THEME = Object.keys(THEMES)[0]

const DESKTOP = merge({}, devices['iPhone 6'], {
  viewport: {
    width: 1220,
    height: 800,
    deviceScaleFactor: 4
  }
});

const MOBILE = merge({}, devices['iPhone 6'], {
  viewport: {
    deviceScaleFactor: 4
  }
});

async function renderScene (blender, { textures, ...context }) {
  const defs = [];
  for (const name of Object.keys(textures)) {
    if (textures[name] !== false) {
      const image = path.join(__dirname, 'build', `${name}.png`);
      defs.push(writeFileAsync(image, textures[name]));
    }
  }

  await Promise.all(defs);
  await blender.run({
    target: __dirname,
    ...context
  });

  return readFileAsync(path.join(__dirname, 'build/blender.png'));
}

async function actionStockPickingTypeKanban (webclient) {
  await webclient.doMenuAction('stock.stock_picking_type_action');
  await timeout(500);
}

async function actionStockPickingForm (webClient) {
  await webClient.doMenuAction('stock.action_picking_tree_all', { view_type: 'form', res_id: 1 });
  await timeout(500);
}

async function actionSaleOrderFormCreate (webClient) {
  await webClient.doMenuAction('sale.action_quotations', { view_type: 'form', res_id: 1 });
  await timeout(500);
  await webClient.page.click('.o_form_button_edit');
  await timeout(500);
  await webClient.page.click('div[name="partner_id"] input');
  await timeout(500);
  await webClient.page.hover('.ui-autocomplete .ui-menu-item:last-child');
}

async function actionSaleOrderFormCreateCustomer (webClient) {
  await webClient.doMenuAction('sale.action_quotations', { view_type: 'form', res_id: 1 });
  await timeout(500);
  await webClient.page.click('.o_form_button_edit');
  await timeout(500);
  await webClient.page.click('div[name="partner_id"] input');
  await timeout(500);
  await webClient.page.click('.ui-autocomplete .ui-menu-item:last-child');
  await timeout(1000);
}

async function actionSaleOrderForm (webClient) {
  await webClient.doMenuAction('sale.action_quotations', { view_type: 'form', res_id: 20 });
  await timeout(500);
}

async function actionSaleOrderKanban (webClient) {
  await webClient.doMenuAction('sale.action_quotations', { view_type: 'kanban' });
  await timeout(500);
}

async function actionFleetVehicleForm (webClient) {
  await webClient.doMenuAction('fleet.fleet_vehicle_action', { view_type: 'form', res_id: 1 });
  await timeout(500);
}

async function actionFleetVehicleKanban (webClient) {
  await webClient.doMenuAction('fleet.fleet_vehicle_action', { view_type: 'kanban' });
  await timeout(500);
}

async function actionHrJobKanban (webClient) {
  await webClient.doMenuAction('hr_recruitment.action_hr_job', { view_type: 'kanban' });
  await timeout(500);
}

async function actionContactKanban (webClient) {
  await webClient.doMenuAction('contacts.action_contacts');
  await timeout(500);
}

async function actionContactForm (webClient) {
  await webClient.doMenuAction('contacts.action_contacts', { view_type: 'form', res_id: 13 });
  await timeout(500);
}

async function actionHrHolidaysCalendar (webClient) {
  await webClient.doMenuAction('hr_holidays.action_hr_holidays_dashboard');
  await timeout(500);
}

async function actionCrmLeadKanban (webClient) {
  await webClient.doMenuAction('crm.action_your_pipeline');
  await timeout(500);
}

async function actionMailChat (webClient) {
  await webClient.doMenuAction('mail.mail_channel_action_client_chat');
  await timeout(500);
}

async function actionBaseModuleKanban (webClient) {
  await webClient.doMenuAction('base.open_module_tree');
  await timeout(500);
}

async function actionProductionOrderForm (webClient) {
  await webClient.doMenuAction('mrp.mrp_production_action', { view_type: 'form', res_id: 1 });
  await timeout(500);
}

async function actionCalendarEvent (webClient) {
  await webClient.doMenuAction('calendar.action_calendar_event');
  await webClient.page.click('.o_calendar_button_month');
  await webClient.page.click('.a_shell');
  await timeout(500);
}

async function actionConfigureTheme (webClient) {
  await webClient.doMenuAction('base_setup.action_general_configuration');
  await webClient.page.click('[data-key="adaptiv_web"]');
  await timeout(500);
}

async function screenshot ({ odoo, action, device, theme }) {
  const webClient = await odoo.webClient({ device, params: { theme } });
  await webClient.toggleAppMenu(false);
  await timeout(1000);
  await action(webClient);
  const screenshot = await webClient.screenshot();
  await webClient.close();
  return screenshot;
}

function doWith(action, { appMenu, menu }) {
  return async (webClient) => {
    await action(webClient);
    if (appMenu) {
      await webClient.toggleAppMenu(true);
      await timeout(500);
    }

    if (menu) {
      await webClient.toggleMenu(true);
      await timeout(500);
    }
  }
}

function getObjects(textures) {
  return reduce(textures, (acc, buffer, name) => {
    if (buffer !== false) {
      acc[name] = {
        material: {
          0: {
            type: 'ShaderNodeTexImage',
            props: {
              'image': `bpy.data.images.load('${path.join(__dirname, 'build', `${name}.png`)}')`
            }
          },
          1: {
            type: 'ShaderNodeBsdfPrincipled',
            inputs: {
              0: '(0.5,0.5,0.5,1)', // Color
              7: 1 // Roughness
            }
          }
        }
      };
    }
    return acc;
  }, {});
}

async function renderMain ({ odoo, blender, theme=DEFAULT_THEME}) {
  const textures = await Promise.props({
    desktop01: screenshot({ odoo, theme, device: DESKTOP, action: actionSaleOrderForm }),
    desktop02: screenshot({ odoo, theme, device: DESKTOP, action: actionContactForm }),
    desktop03: screenshot({ odoo, theme, device: DESKTOP, action: actionStockPickingTypeKanban }),
    desktop04: screenshot({ odoo, theme, device: DESKTOP, action: doWith(actionContactForm, { appMenu: true }) }),
    mobile01: screenshot({ odoo, theme, device: MOBILE, action: actionSaleOrderKanban }),
    mobile02: screenshot({ odoo, theme, device: MOBILE, action: actionContactForm }),
    mobile03: screenshot({ odoo, theme, device: MOBILE, action: doWith(actionContactForm, { appMenu: true }) }),
  });

  let image = await renderScene(blender, merge({}, SCENE_DEFAULTS, THEMES[theme], {
    textures,
    scene: path.join(__dirname, 'scenes/splash.dae'),
    outputWidth: 1024,
    outputHeight: 512,
    objects: {
      ...getObjects(textures, {

      }),
      camera: {
        data: {
          lens: 182,
          sensor_width: 170
        }
      }
    }
  }));

  return image;
}

async function renderMainScreenshot ({ odoo, blender, theme=DEFAULT_THEME }) {
  // 0.228, 0.146, 0.805
  const textures = await Promise.props({
    mobile01: screenshot({ odoo, theme, device: MOBILE, action: actionSaleOrderKanban }),
    mobile02: screenshot({ odoo, theme, device: MOBILE, action: actionContactForm }),
    mobile03: screenshot({ odoo, theme, device: MOBILE, action: doWith(actionContactForm, { appMenu: true }) }),
  });

  let image = await renderScene(blender, merge({}, SCENE_DEFAULTS, THEMES[theme], {
    textures,
    scene: path.join(__dirname, 'scenes/screenshot.dae'),
    outputWidth: 365,
    outputHeight: 460,
    objects: {
      ...getObjects(textures, {

      }),
      camera: {
        data: {
          lens: 182,
          sensor_width: 170
        }
      }
    }
  }));

  return image;
}



async function renderSplash ({ odoo, blender, theme=DEFAULT_THEME }) {
  const textures = await Promise.props({
    desktop01: screenshot({ odoo, theme, device: DESKTOP, action: actionSaleOrderForm }),
    desktop02: screenshot({ odoo, theme, device: DESKTOP, action: actionContactForm }),
    desktop03: screenshot({ odoo, theme, device: DESKTOP, action: actionStockPickingTypeKanban }),
    desktop04: screenshot({ odoo, theme, device: DESKTOP, action: doWith(actionContactForm, { appMenu: true }) }),
    mobile01: screenshot({ odoo, theme, device: MOBILE, action: actionSaleOrderKanban }),
    mobile02: screenshot({ odoo, theme, device: MOBILE, action: actionContactForm }),
    mobile03: screenshot({ odoo, theme, device: MOBILE, action: doWith(actionContactForm, { appMenu: true }) }),
  });

  let image = await renderScene(blender, merge({}, SCENE_DEFAULTS, THEMES[theme], {
    textures,
    scene: path.join(__dirname, 'scenes/splash.dae'),
    outputWidth: 1200,
    outputHeight: 600,
    objects: {
      ...getObjects(textures, {

      }),
      camera: {
        data: {
          lens: 182,
          sensor_width: 170
        }
      }
    }
  }));

  return image;
}

async function renderThemes ({ odoo, blender }) {

  const textures = await Promise.props({
    mobile01: screenshot({ odoo, theme: DEFAULT_THEME, device: MOBILE, action: actionSaleOrderKanban }),
    mobile02: screenshot({ odoo, theme: 'odoo', device: MOBILE, action: actionSaleOrderKanban }),
    mobile03: screenshot({ odoo, theme: 'industrial', device: MOBILE, action: actionSaleOrderKanban }),
    mobile04: screenshot({ odoo, theme: 'candy', device: MOBILE, action: actionSaleOrderKanban }),
    mobile05: screenshot({ odoo, theme: 'emerald', device: MOBILE, action: actionSaleOrderKanban }),
    mobile06: screenshot({ odoo, theme: 'brave', device: MOBILE, action: actionSaleOrderKanban }),
  });

  let image = await renderScene(blender, merge({}, SCENE_DEFAULTS, THEMES[DEFAULT_THEME], {
    textures,
    scene: path.join(__dirname, 'scenes/themes.dae'),
    outputWidth: 1200,
    outputHeight: 600,
    objects: {
      ...getObjects(textures)
    }
  }));

  return image;
}

async function renderShell ({ odoo, blender, theme=DEFAULT_THEME }) {

  const textures = await Promise.props({
    desktop01: screenshot({ odoo, theme, device: DESKTOP, action: actionSaleOrderFormCreate }),
    desktop02: screenshot({ odoo, theme, device: DESKTOP, action: actionSaleOrderFormCreateCustomer })
  });

  let image = await renderScene(blender, merge({}, SCENE_DEFAULTS, THEMES[theme], {
    textures,
    scene: path.join(__dirname, 'scenes/shell.dae'),
    outputWidth: 1200,
    outputHeight: 600,
    objects: {
      ...getObjects(textures)
    }
  }));

  return image;
}


async function renderScreen ({ odoo, blender, action, theme=DEFAULT_THEME }) {

  const textures = await Promise.props({
    desktop01: screenshot({ odoo, theme, device: DESKTOP, action }),
    mobile01: screenshot({ odoo, theme, device: MOBILE, action })
  });

  let image = await renderScene(blender, merge({}, SCENE_DEFAULTS, THEMES[theme], {
    textures,
    scene: path.join(__dirname, 'scenes/screen.dae'),
    outputWidth: 1200,
    outputHeight: 600,
    objects: {
      ...getObjects(textures)
    }
  }));

  return image;
}

async function renderLogin ({ browser, theme=DEFAULT_THEME }) {

  const width = 1400;
  const height = 800;
  const device = merge({}, devices['iPhone 6'], {
    viewport: {
      width,
      height,
      deviceScaleFactor: 1
    }
  })

  const page = await browser.newPage();
  await page.emulate(device);
  let qs = querystring.stringify({ db: 'demo' });
  let target = urlJoin('http://localhost:8000/web/login', `?${qs}`);
  await page.goto(target);
  qs = querystring.stringify({ theme });
  target = urlJoin('http://localhost:8000/web/login', `?${qs}`);
  await page.goto(target);
  const image = await page.screenshot();
  await page.close();

  return image;
}


const screens = [
  {
    name: 'Chat',
    action: actionMailChat
  },
  {
    name: 'Calendar',
    action: actionCalendarEvent
  },
  {
    name: 'Contact Kanban',
    action: actionContactKanban
  },
  {
    name: 'Contact Form',
    action: actionContactKanban
  },
  {
    name: 'Sale Order Kanban',
    action: actionSaleOrderKanban
  },
  {
    name: 'Sale Order Form',
    action: actionSaleOrderForm
  },
  {
    name: 'Fleet Vehicle Kanban',
    action: actionFleetVehicleKanban
  },
  {
    name: 'Fleet Vehicle Form',
    action: actionFleetVehicleForm
  },
  {
    name: 'Production Order Form',
    action: actionProductionOrderForm
  },
  {
    name: 'HR Job Kanban',
    action: actionHrJobKanban
  },
  {
    name: 'HR Holidays Calendar',
    action: actionHrHolidaysCalendar
  },
  {
    name: 'Applications',
    action: actionBaseModuleKanban
  },
  {
    name: 'Configure Theme',
    action: actionConfigureTheme
  },
  {
    name: 'App Menu',
    action: doWith(actionContactForm, { appMenu: true })
  }
]

module.exports = {
  screens,
  themes: THEMES,
  images: {
    'main.png': async (args) => {
      return sharp(await renderMain({ ...args })).toBuffer();
    },
    'main_screenshot.png': async (args) => {
      return sharp(await renderMainScreenshot({ ...args })).toBuffer();
    },
    'dist/splash.png': async (args) => {
      return sharp(await renderSplash({ ...args })).toBuffer();
    },
    'dist/themes.png': async (args) => {
      return sharp(await renderThemes({ ...args })).toBuffer();
    },
    'dist/shell.png': async (args) => {
      return sharp(await renderShell({ ...args })).toBuffer();
    },
    ...reduce(Object.keys(THEMES), (acc, theme, index) => ({
      ...acc,
      [`dist/login_${theme}.png`]: async (args) => {
        return sharp(await renderLogin({ theme, ...args })).toBuffer();
      },
      [`dist/login_${theme}_thumb.png`]: {
        inputs: [`dist/login_${theme}.png`],
        generate: async ({ inputs, ...args }) => {
          return sharp(inputs[`dist/login_${theme}.png`]).resize(300).toBuffer();
        }
      }
    }), {}),
    ...reduce(Object.keys(THEMES), (acc, theme, index) => (
      reduce(screens, (acc, screen, index) => ({
        ...acc,
        [`dist/${theme}_screen_${index + 1}.png`]: async (args) => {
          return sharp(await renderScreen({ action: screen.action, theme, ...args })).toBuffer();
        },
        [`dist/${theme}_screen_${index + 1}_thumb.png`]: {
          inputs: [`dist/${theme}_screen_${index + 1}.png`],
          generate: async ({ inputs, ...args }) => {
            return sharp(inputs[`dist/${theme}_screen_${index + 1}.png`]).resize(300).toBuffer();
          }
        }
      }), acc)
    ), {}),
  }
};
