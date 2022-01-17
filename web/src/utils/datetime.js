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


export const toRelativeDate = (previous) => {
  const current = new Date();

  const msPerMinute = 60 * 1000;
  const msPerHour = msPerMinute * 60;
  const msPerDay = msPerHour * 24;
  const msPerMonth = msPerDay * 30;
  const msPerYear = msPerDay * 365;

  const elapsed = current - previous;

  if (elapsed < msPerMinute) {
    return Math.round(elapsed/1000) + ' seconds ago';
  } else if (elapsed < msPerHour) {
    return Math.round(elapsed/msPerMinute) + ' minutes ago';
  } else if (elapsed < msPerDay ) {
    return Math.round(elapsed/msPerHour ) + ' hours ago';
  } else if (elapsed < msPerMonth) {
    return Math.round(elapsed/msPerDay) + ' days ago';
  } else if (elapsed < msPerYear) {
    return Math.round(elapsed/msPerMonth) + ' months ago';
  } else {
    return Math.round(elapsed/msPerYear ) + ' years ago';
  }
};

