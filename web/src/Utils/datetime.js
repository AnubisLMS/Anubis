export const nonStupidDatetimeFormat = (date) => (
  `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()} ` +
  `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`
);
