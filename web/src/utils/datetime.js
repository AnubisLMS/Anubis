export const nonStupidDatetimeFormat = (date) => {
  let seconds = date.getSeconds().toString();
  let minutes = date.getMinutes().toString();
  let hours = date.getHours().toString();
  let day = date.getDate().toString();
  let months = (date.getMonth() + 1).toString();
  const year = date.getFullYear().toString();

  if (seconds.length === 1) {
    seconds = '0' + seconds;
  }
  if (minutes.length === 1) {
    minutes = '0' + minutes;
  }
  if (hours.length === 1) {
    hours = '0' + hours;
  }
  if (day.length === 1) {
    day = '0' + day;
  }
  if (months.length === 1) {
    months = '0' + months;
  }

  return `${year}-${months}-${day} ${hours}:${minutes}:${seconds}`;
};
