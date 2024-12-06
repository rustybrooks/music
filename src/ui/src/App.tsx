import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '@mantine/dates/styles.css';
import { Route, Routes } from 'react-router';
import { AppShell, createTheme, MantineProvider, rem } from '@mantine/core';
import { useCallback, useEffect, useState } from 'react';
import { Header } from './components/Header';
import { NavBar } from './components/NavBar';
import { Home } from './views/Home';
import { MidiContext, MidiContextType } from './contexts/MidiContext';
import { CallbackMap, MidiInputs, MidiMessage, MidiOutputs } from './types';
import { Torso } from './components/sequencers/Torso';

const theme = createTheme({
  //
  // /** Controls focus ring styles. Supports the following options:
  //  *  - `auto` – focus ring is displayed only when the user navigates with keyboard (default value)
  //  *  - `always` – focus ring is displayed when the user navigates with keyboard and mouse
  //  *  - `never` – focus ring is always hidden (not recommended)
  //  */
  // focusRing: 'auto' | 'always' | 'never';
  //
  // /** rem units scale, change if you customize font-size of `<html />` element
  //  *  default value is `1` (for `100%`/`16px` font-size on `<html />`)
  //  */
  scale: 1,
  //
  // /** Determines whether `font-smoothing` property should be set on the body, `true` by default */
  fontSmoothing: true,
  //
  // /** White color */
  white: '#ffffff',
  //
  // /** Black color */
  black: '#402000',
  //
  // /** Object of colors, key is color name, value is an array of at least 10 strings (colors) */
  // There is supposed to be 10 variants per color, these are just copies

  //
  // /** Index of theme.colors[color].
  //  *  Primary shade is used in all components to determine which color from theme.colors[color] should be used.
  //  *  Can be either a number (0–9) or an object to specify different color shades for light and dark color schemes.
  //  *  Default value `{ light: 6, dark: 8 }`
  //  *
  //  *  For example,
  //  *  { primaryShade: 6 } // shade 6 is used both for dark and light color schemes
  //  *  { primaryShade: { light: 6, dark: 7 } } // different shades for dark and light color schemes
  //  * */
  // primaryShade: 1,
  //
  // /** Key of `theme.colors`, hex/rgb/hsl values are not supported.
  //  *  Determines which color will be used in all components by default.
  //  *  Default value – `blue`.
  //  * */
  // primaryColor: "dm-green",
  //
  // /** Function to resolve colors based on variant.
  //  *  Can be used to deeply customize how colors are applied to `Button`, `ActionIcon`, `ThemeIcon`
  //  *  and other components that use colors from theme.
  //  * */
  // variantColorResolver: VariantColorsResolver;
  //
  // /** Determines whether text color must be changed based on the given `color` prop in filled variant
  //  *  For example, if you pass `color="blue.1"` to Button component, text color will be changed to `var(--mantine-color-black)`
  //  *  Default value – `false`
  //  * */
  // autoContrast: boolean;
  //
  // /** Determines which luminance value is used to determine if text color should be light or dark.
  //  *  Used only if `theme.autoContrast` is set to `true`.
  //  *  Default value is `0.3`
  //  * */
  // luminanceThreshold: number;
  //
  // /** font-family used in all components, system fonts by default */
  fontFamily: 'Red Hat Display',
  //
  // /** Monospace font-family, used in code and other similar components, system fonts by default  */
  fontFamilyMonospace: 'Red Hat Mono',
  //
  // /** Controls various styles of h1-h6 elements, used in TypographyStylesProvider and Title components */
  headings: {
    fontFamily: 'Oxanium',
    // fontWeight: string;
    // textWrap: 'wrap' | 'nowrap' | 'balance' | 'pretty' | 'stable';
    // sizes: {
    //     h1: HeadingStyle;
    //     h2: HeadingStyle;
    //     h3: HeadingStyle;
    //     h4: HeadingStyle;
    //     h5: HeadingStyle;
    //     h6: HeadingStyle;
    // };
  },
  //
  // /** Object of values that are used to set `border-radius` in all components that support it */
  // radius: MantineRadiusValues;
  //
  // /** Key of `theme.radius` or any valid CSS value. Default `border-radius` used by most components */
  // defaultRadius: MantineRadius;
  //
  // /** Object of values that are used to set various CSS properties that control spacing between elements */
  // spacing: MantineSpacingValues;
  //
  // /** Object of values that are used to control `font-size` property in all components */
  // fontSizes: MantineFontSizesValues;
  //
  // /** Object of values that are used to control `line-height` property in `Text` component */
  // lineHeights: MantineLineHeightValues;
  //
  // /** Object of values that are used to control breakpoints in all components,
  //  *  values are expected to be defined in em
  //  * */
  // breakpoints: MantineBreakpointsValues;
  //
  // /** Object of values that are used to add `box-shadow` styles to components that support `shadow` prop */
  // shadows: MantineShadowsValues;
  //
  // /** Determines whether user OS settings to reduce motion should be respected, `false` by default */
  // respectReducedMotion: boolean;
  //
  // /** Determines which cursor type will be used for interactive elements
  //  * - `default` – cursor that is used by native HTML elements, for example, `input[type="checkbox"]` has `cursor: default` styles
  //  * - `pointer` – sets `cursor: pointer` on interactive elements that do not have these styles by default
  //  */
  // cursorType: 'default' | 'pointer';
  //
  // /** Default gradient configuration for components that support `variant="gradient"` */
  // defaultGradient: MantineGradient;
  //
  // /** Class added to the elements that have active styles, for example, `Button` and `ActionIcon` */
  // activeClassName: string;
  //
  // /** Class added to the elements that have focus styles, for example, `Button` or `ActionIcon`.
  //  *  Overrides `theme.focusRing` property.
  //  */
  // focusClassName: string;
  //
  // /** Allows adding `classNames`, `styles` and `defaultProps` to any component */
  // components: MantineThemeComponents;
  //
  // /** Any other properties that you want to access with the theme objects */
  // other: MantineThemeOther;
});

const NoMatch = () => {
  return <div>(No Match)</div>;
};

export const App = () => {
  const [midiContext, setMidiContext] = useState<MidiContextType>({
    midiInputs: {},
    midiOutputs: {},
    midiAccess: null,
    midiCallbackMap: {},
  });

  const callback = (m: any) => {
    const message = new MidiMessage(m);
    const midi_id = m.target.id;
    if (Object.keys(midiContext.midiCallbackMap[midi_id]).length) {
      console.log(m);
      console.log('midi cb', midi_id, midiContext.midiCallbackMap[midi_id]);
      Object.values(midiContext.midiCallbackMap[midi_id]).forEach(cb => {
        cb(message);
      });
    }
  };

  const onChangeCallback = useCallback(
    (access: any, e: any) => {
      // console.log('onstatechange', e);
      console.log(e.port.id, e.port.name, e.port.state, e.port.type, e.port.connection);
      if (e.port.type === 'input') {
        if (e.port.state === 'connected') {
          setMidiContext({ ...midiContext, midiInputs: { ...midiContext.midiInputs, [e.port.id]: e.port } });
        } else {
          setMidiContext({
            ...midiContext,
            midiInputs: Object.fromEntries(Object.entries(midiContext.midiInputs).filter(entry => entry[0] !== e.port.id)),
          });
        }
      } else if (e.port.state === 'connected') {
        e.port.object = access.outputs.get(e.port.id);
        setMidiContext({ ...midiContext, midiOutputs: { ...midiContext.midiOutputs, [e.port.id]: e.port } });
      } else {
        setMidiContext({
          ...midiContext,
          midiOutputs: Object.fromEntries(Object.entries(midiContext.midiOutputs).filter(entry => entry[0] !== e.port.id)),
        });
      }
    },
    [midiContext],
  );

  const accessCallback = (access: any) => {
    const midiInputs: MidiInputs = {};
    const midiOutputs: MidiOutputs = {};
    const midiCallbackMap: CallbackMap = {};

    for (const input of access.inputs.values()) {
      input.onmidimessage = callback;
      midiCallbackMap[input.id] = {};
      midiInputs[input.id] = input;
    }

    for (const output of access.outputs.values()) {
      output.onmidimessage = callback;
      output.object = access.outputs.get(output.id);
      midiCallbackMap[output.id] = {};
      midiOutputs[output.id] = output;
    }

    setMidiContext({
      ...midiContext,
      midiInputs,
      midiOutputs,
      midiAccess: access,
      midiCallbackMap: { ...midiContext.midiCallbackMap, ...midiCallbackMap },
    });

    access.onstatechange = (e: any) => onChangeCallback(access, e);
  };

  const init = () => {
    navigator.requestMIDIAccess().then(accessCallback);
  };

  // const listen = (midi_id: number, listen_id: number, cb: MidiCallback) => {
  //   // console.log('listen', midi_id, callback)
  //   midiCallbackMap[midi_id][listen_id] = cb;
  // };

  useEffect(() => {
    init();
  }, []);

  return (
    <MantineProvider defaultColorScheme="auto" theme={theme}>
      <MidiContext.Provider value={midiContext}>
        <AppShell
          withBorder={false}
          padding="md"
          header={{ height: '50px', offset: true }}
          footer={{ height: 0 }}
          navbar={{
            width: rem('80px'),
            breakpoint: 'sm',
          }}
        >
          <AppShell.Header>
            <Header />
          </AppShell.Header>
          <AppShell.Navbar p="md">
            <NavBar />
          </AppShell.Navbar>
          <AppShell.Main>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/torso" element={<Torso />} />
              <Route element={<NoMatch />} />
            </Routes>
          </AppShell.Main>
        </AppShell>
      </MidiContext.Provider>
    </MantineProvider>
  );
};
