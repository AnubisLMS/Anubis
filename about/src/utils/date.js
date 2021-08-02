import dateFormat from 'dateformat';

export const formatDate = (date) => {
  const tempDate = new Date(date);
  return dateFormat(tempDate, "dddd, mmmm dS, yyyy");
}