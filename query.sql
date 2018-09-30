/*
Top songs by len_gzip
*/
SELECT artist.name, song.name, lyric, len_gzip, len, 1.0 * len_gzip / len
FROM song
JOIN artist ON artist.id == song.artist_id
WHERE len_gzip IS NOT NULL
ORDER BY len_gzip DESC
LIMIT 100